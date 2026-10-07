from __future__ import annotations
from .prompt import build_bashrc
import re
import socket
from typing import Sequence

import docker
from docker.errors import APIError, NotFound

from .provider import (
    RuntimeCommandResult,
    RuntimeMachine,
    RuntimeMachineLimits,
    RuntimeNetwork,
    RuntimeNetworkAttachment,
    RuntimeProvider,
    RuntimeRoute,
    RuntimeShell,
)

MANAGED_LABELS = {"nightbreach.managed": "true"}

# Hosts, ports and destinations are interpolated into shell commands executed
# inside containers, so they are strictly validated before use.
_HOST_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
_CIDR_PATTERN = re.compile(r"^[0-9]{1,3}(\.[0-9]{1,3}){3}(/[0-9]{1,2})?$")
_INTERFACE_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,15}$")


class DockerRuntimeError(RuntimeError):
    """Base error for Docker runtime operations."""


class DockerRuntimeProvider(RuntimeProvider):
    """Docker implementation of the Sandbox RuntimeProvider."""

    def __init__(self, client: docker.DockerClient | None = None) -> None:
        self.client = client or docker.from_env()

    def create_network(
        self,
        *,
        name: str,
        subnet: str | None = None,
        gateway: str | None = None,
        internal: bool = True,
    ) -> RuntimeNetwork:
        ipam_config = None

        if subnet is not None:
            pool_kwargs: dict[str, str] = {"subnet": subnet}

            if gateway is not None:
                pool_kwargs["gateway"] = gateway

            ipam_config = docker.types.IPAMConfig(
                pool_configs=[docker.types.IPAMPool(**pool_kwargs)]
            )

        try:
            # internal=True removes outbound NAT: lab machines can talk to
            # each other but not to the internet or the host's networks.
            network = self.client.networks.create(
                name=name,
                driver="bridge",
                ipam=ipam_config,
                internal=internal,
                labels=dict(MANAGED_LABELS),
            )
        except APIError as exc:
            raise DockerRuntimeError(
                f"Failed to create Docker network '{name}'."
            ) from exc

        return RuntimeNetwork(
            id=network.id,
            name=network.name,
        )

    def remove_network(self, *, network_id: str) -> None:
        try:
            network = self.client.networks.get(network_id)
            network.remove()
        except NotFound:
            return
        except APIError as exc:
            raise DockerRuntimeError(
                f"Failed to remove Docker network '{network_id}'."
            ) from exc

    def create_machine(
        self,
        *,
        name: str,
        image: str,
        network_attachments: Sequence[RuntimeNetworkAttachment],
        limits: RuntimeMachineLimits | None = None,
        command: Sequence[str] | None = None,
        hostname: str | None = None,
    ) -> RuntimeMachine:
        if not network_attachments:
            raise DockerRuntimeError(
                "A machine requires at least one network attachment."
            )

        limits = limits or RuntimeMachineLimits()
        container_id: str | None = None

        try:
            networks = [
                self.client.networks.get(attachment.network_id)
                for attachment in network_attachments
            ]
            first_network = networks[0]

            host_config = self.client.api.create_host_config(
                # Created directly on the lab network, never on the default
                # bridge, so there is no path to other labs or the host.
                network_mode=first_network.name,
                mem_limit=limits.memory,
                memswap_limit=limits.memory,
                nano_cpus=int(limits.cpus * 1_000_000_000),
                pids_limit=limits.pids,
                cap_drop=["ALL"],
                cap_add=list(limits.capabilities),
                security_opt=(
                    ["no-new-privileges:true"]
                    if limits.no_new_privileges
                    else []
                ),
                privileged=False,
                read_only=limits.read_only_rootfs,
                tmpfs=(
                    {"/tmp": "rw,nosuid,size=64m"}
                    if limits.read_only_rootfs
                    else None
                ),
                init=True,
                ipc_mode="private",
                restart_policy={"Name": "no"},
                log_config=docker.types.LogConfig(
                    type=docker.types.LogConfig.types.JSON,
                    config={"max-size": "1m", "max-file": "1"},
                ),
            )

            networking_config = self.client.api.create_networking_config(
                {
                    first_network.name: self.client.api.create_endpoint_config(
                        ipv4_address=network_attachments[0].ipv4_address,
                    )
                }
            )

            response = self.client.api.create_container(
                image=image,
                command=list(command) if command else None,
                name=name,
                hostname=hostname or name,
                user=limits.user,
                labels=dict(MANAGED_LABELS),
                host_config=host_config,
                networking_config=networking_config,
                stdin_open=True,
                tty=True,
                detach=True,
            )
            container_id = response["Id"]
            container = self.client.containers.get(container_id)

            for attachment, network in zip(
                network_attachments[1:],
                networks[1:],
            ):
                connect_kwargs = {}

                if attachment.ipv4_address is not None:
                    connect_kwargs["ipv4_address"] = attachment.ipv4_address

                network.connect(container, **connect_kwargs)

        except (APIError, NotFound) as exc:
            if container_id is not None:
                try:
                    self.client.containers.get(container_id).remove(
                        force=True
                    )
                except (APIError, NotFound):
                    pass

            raise DockerRuntimeError(
                f"Failed to create Docker machine '{name}'."
            ) from exc

        return RuntimeMachine(
            id=container.id,
            name=container.name,
        )

    def start_machine(self, *, machine_id: str) -> None:
        try:
            container = self.client.containers.get(machine_id)
            container.start()
        except (APIError, NotFound) as exc:
            raise DockerRuntimeError(
                f"Failed to start Docker machine '{machine_id}'."
            ) from exc

    def configure_route(
        self,
        *,
        machine_id: str,
        destination: str,
        gateway: str | None = None,
        interface: str | None = None,
    ) -> None:
        if not _CIDR_PATTERN.fullmatch(destination):
            raise DockerRuntimeError(
                f"Invalid route destination '{destination}'."
            )

        if gateway is not None and not _HOST_PATTERN.fullmatch(gateway):
            raise DockerRuntimeError(f"Invalid route gateway '{gateway}'.")

        if interface is not None and not _INTERFACE_PATTERN.fullmatch(
            interface
        ):
            raise DockerRuntimeError(
                f"Invalid route interface '{interface}'."
            )

        argv = ["ip", "route", "replace", destination]

        if gateway is not None:
            argv.extend(["via", gateway])

        if interface is not None:
            argv.extend(["dev", interface])

        # Routes are programmed from inside the container, as root: adding a
        # route needs CAP_NET_ADMIN, which the container's default user may
        # not hold even when the capability is granted to the container.
        result = self._exec_argv(machine_id, argv, user="root")

        if result.exit_code != 0:
            detail = (result.stderr or result.stdout).strip()
            raise DockerRuntimeError(
                f"Failed to configure route '{destination}' on Docker "
                f"machine '{machine_id}': {detail or 'ip route failed'}"
            )

    def inspect_routes(self, *, machine_id: str) -> tuple[RuntimeRoute, ...]:
        result = self._exec_argv(
            machine_id,
            ["ip", "-j", "route"],
            user="root",
        )

        if result.exit_code == 0:
            return self._parse_json_routes(result.stdout)

        result = self._exec_argv(
            machine_id,
            ["ip", "route"],
            user="root",
        )

        if result.exit_code != 0:
            detail = (result.stderr or result.stdout).strip()
            raise DockerRuntimeError(
                f"Failed to inspect routes on Docker machine "
                f"'{machine_id}': {detail or 'ip route failed'}"
            )

        return self._parse_text_routes(result.stdout)

    @staticmethod
    def _parse_json_routes(stdout: str) -> tuple[RuntimeRoute, ...]:
        import json

        try:
            entries = json.loads(stdout)
        except ValueError as exc:
            raise DockerRuntimeError(
                "Runtime returned an unreadable route table."
            ) from exc

        routes: list[RuntimeRoute] = []

        if not isinstance(entries, list):
            raise DockerRuntimeError(
                "Runtime returned an unreadable route table."
            )

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            destination = entry.get("dst") or ""

            if destination in ("default", ""):
                destination = "0.0.0.0/0"

            routes.append(
                RuntimeRoute(
                    destination=destination,
                    gateway=entry.get("gw"),
                    interface=entry.get("dev"),
                )
            )

        return tuple(routes)

    @staticmethod
    def _parse_text_routes(stdout: str) -> tuple[RuntimeRoute, ...]:
        routes: list[RuntimeRoute] = []

        for line in stdout.splitlines():
            parts = line.split()

            if not parts:
                continue

            destination = parts[0]

            if destination == "default":
                destination = "0.0.0.0/0"

            gateway = None
            interface = None

            if "via" in parts:
                index = parts.index("via")

                if index + 1 < len(parts):
                    gateway = parts[index + 1]

            if "dev" in parts:
                index = parts.index("dev")

                if index + 1 < len(parts):
                    interface = parts[index + 1]

            routes.append(
                RuntimeRoute(
                    destination=destination,
                    gateway=gateway,
                    interface=interface,
                )
            )

        return tuple(routes)

    def probe_service(
        self,
        *,
        machine_id: str,
        host: str,
        port: int,
        protocol: str = "tcp",
    ) -> bool:
        if not _HOST_PATTERN.fullmatch(host):
            raise DockerRuntimeError(f"Invalid probe host '{host}'.")

        if not isinstance(port, int) or not 1 <= port <= 65535:
            raise DockerRuntimeError(f"Invalid probe port '{port}'.")

        if protocol == "tcp":
            script = f"exec 3<>/dev/tcp/{host}/{port}"
        elif protocol == "udp":
            # UDP has no handshake; a successful datagram send is the
            # strongest portable readiness signal from inside a container.
            script = f"exec 3<>/dev/udp/{host}/{port} && printf x >&3"
        else:
            raise DockerRuntimeError(f"Unsupported probe protocol '{protocol}'.")

        result = self._exec_argv(
            machine_id,
            ["bash", "-c", script],
        )
        return result.exit_code == 0

    def ping(self, *, machine_id: str, host: str) -> bool:
        if not _HOST_PATTERN.fullmatch(host):
            raise DockerRuntimeError(f"Invalid ping host '{host}'.")

        result = self._exec_argv(
            machine_id,
            ["ping", "-c", "1", "-W", "3", host],
        )
        return result.exit_code == 0

    def _exec_argv(
        self,
        machine_id: str,
        argv: Sequence[str],
        user: str | None = None,
    ) -> RuntimeCommandResult:
        try:
            container = self.client.containers.get(machine_id)
            result = container.exec_run(
                list(argv),
                stdout=True,
                stderr=True,
                user=user,
            )
        except (APIError, NotFound) as exc:
            raise DockerRuntimeError(
                f"Failed to execute command on Docker machine "
                f"'{machine_id}'."
            ) from exc

        output = result.output

        if isinstance(output, tuple):
            stdout = output[0] or b""
            stderr = output[1] or b""
        else:
            stdout = output or b""
            stderr = b""

        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")

        return RuntimeCommandResult(
            exit_code=int(result.exit_code),
            stdout=stdout,
            stderr=stderr,
        )

    def stop_machine(self, *, machine_id: str) -> None:
        try:
            container = self.client.containers.get(machine_id)
            container.stop()
        except NotFound:
            return
        except APIError as exc:
            raise DockerRuntimeError(
                f"Failed to stop Docker machine '{machine_id}'."
            ) from exc

    def remove_machine(self, *, machine_id: str) -> None:
        try:
            container = self.client.containers.get(machine_id)
            container.remove(force=True)
        except NotFound:
            return
        except APIError as exc:
            raise DockerRuntimeError(
                f"Failed to remove Docker machine '{machine_id}'."
            ) from exc

    def inspect_machine(self, *, machine_id: str) -> dict:
        try:
            container = self.client.containers.get(machine_id)
            return container.attrs
        except (APIError, NotFound) as exc:
            raise DockerRuntimeError(
                f"Failed to inspect Docker machine '{machine_id}'."
            ) from exc

    def inspect_network(self, *, network_id: str) -> dict:
        try:
            network = self.client.networks.get(network_id)
            return network.attrs
        except (APIError, NotFound) as exc:
            raise DockerRuntimeError(
                f"Failed to inspect Docker network '{network_id}'."
            ) from exc

    def execute_command(
        self,
        *,
        machine_id: str,
        command: Sequence[str],
        timeout: int | None = None,
    ) -> RuntimeCommandResult:
        if not command:
            raise DockerRuntimeError(
                "A command is required for runtime execution."
            )

        # Docker's exec API has no portable per-command timeout; callers
        # bound runtime with the command itself (e.g. ping -W).
        return self._exec_argv(machine_id, command)

    def open_shell(
        self,
        *,
        machine_id: str,
        username: str | None = None,
        command: Sequence[str] = ("/bin/bash", "-i"),
        environment: dict[str, str] | None = None,
    ) -> RuntimeShell:
        exec_environment = {"TERM": "xterm-256color"}

        if environment:
            exec_environment.update(environment)

        try:
            container = self.client.containers.get(machine_id)
            argv = list(command)

            if username is not None:
                # Inject the NightBreach learner prompt as a per-session
                # bashrc inside the container. The image itself is never
                # modified and the username never enters a shell string.
                bashrc_path = "/tmp/nightbreach.bashrc"
                payload = build_bashrc(username)

                container.put_archive(
                    path="/tmp",
                    data=_tar_with_file(
                        "nightbreach.bashrc",
                        payload.encode("utf-8"),
                    ),
                )

                argv = ["/bin/bash", "--rcfile", bashrc_path, "-i"]

            exec_id = self.client.api.exec_create(
                container.id,
                argv,
                tty=True,
                stdin=True,
                environment=exec_environment,
            )["Id"]

            stream = self.client.api.exec_start(
                exec_id, tty=True, socket=True
            )

            return DockerShell(
                client=self.client,
                exec_id=exec_id,
                stream=stream,
            )
        except APIError as error:
            raise DockerRuntimeError("Failed to open a shell.") from error


def _tar_with_file(name: str, content: bytes) -> bytes:
    """Build a minimal in-memory tar containing one file."""
    import io
    import tarfile

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        info = tarfile.TarInfo(name=name)
        info.size = len(content)
        archive.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


class DockerShell(RuntimeShell):
    """Interactive exec session over Docker's hijacked connection."""

    def __init__(self, *, client, exec_id: str, stream) -> None:
        self._client = client
        self._exec_id = exec_id
        self._stream = stream
        self._raw = getattr(stream, "_sock", stream)
        self._closed = False

    def read(self) -> bytes | None:
        if self._closed:
            return None

        try:
            data = self._raw.recv(4096)
        except (OSError, ValueError):
            return None

        return data or None

    def write(self, data: bytes) -> None:
        if self._closed:
            return

        try:
            self._raw.sendall(data)
        except (OSError, ValueError) as exc:
            raise DockerRuntimeError("Terminal connection closed.") from exc

    def resize(self, cols: int, rows: int) -> None:
        try:
            self._client.api.exec_resize(
                self._exec_id,
                height=rows,
                width=cols,
            )
        except (APIError, NotFound):
            pass

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        # shutdown() wakes a thread blocked in recv(); close() alone may not.
        try:
            self._raw.shutdown(socket.SHUT_RDWR)
        except (OSError, AttributeError):
            pass

        for handle in (self._raw, self._stream):
            try:
                handle.close()
            except Exception:
                pass
