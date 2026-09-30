from __future__ import annotations

from typing import Sequence

import docker
from docker.errors import APIError, NotFound

from .provider import (
    RuntimeMachine,
    RuntimeNetwork,
    RuntimeNetworkAttachment,
    RuntimeProvider,
)


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
    ) -> RuntimeNetwork:
        ipam_pool = None

        if subnet is not None:
            pool_kwargs: dict[str, str] = {"subnet": subnet}

            if gateway is not None:
                pool_kwargs["gateway"] = gateway

            ipam_pool = docker.types.IPAMPool(**pool_kwargs)

        ipam_config = None

        if ipam_pool is not None:
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        try:
            network = self.client.networks.create(
                name=name,
                driver="bridge",
                ipam=ipam_config,
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
    ) -> RuntimeMachine:
        try:
            container = self.client.containers.create(
                image=image,
                name=name,
                detach=True,
            )

            for attachment in network_attachments:
                network = self.client.networks.get(
                    attachment.network_id
                )

                connect_kwargs = {}

                if attachment.ipv4_address is not None:
                    connect_kwargs["ipv4_address"] = (
                        attachment.ipv4_address
                    )

                network.connect(
                    container,
                    **connect_kwargs,
                )

        except (APIError, NotFound) as exc:
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
