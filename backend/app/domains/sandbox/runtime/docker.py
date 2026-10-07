from __future__ import annotations
from .prompt import build_bashrc
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
    RuntimeShell,
)

MANAGED_LABELS = {"nightbreach.managed": "true"}


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

        try:
            container = self.client.containers.get(machine_id)

            # Docker's exec API has no portable per-command timeout; callers
            # bound runtime with the command itself (e.g. ping -W).
            result = container.exec_run(
                list(command),
                stdout=True,
                stderr=True,
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
