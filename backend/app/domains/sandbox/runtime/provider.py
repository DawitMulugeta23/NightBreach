from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class RuntimeNetwork:
    id: str
    name: str


@dataclass(frozen=True)
class RuntimeMachine:
    id: str
    name: str


@dataclass(frozen=True)
class RuntimeNetworkAttachment:
    network_id: str
    ipv4_address: str | None = None


class RuntimeProvider(ABC):
    """Logical runtime interface owned by the Sandbox domain."""

    @abstractmethod
    def create_network(
        self,
        *,
        name: str,
        subnet: str | None = None,
        gateway: str | None = None,
    ) -> RuntimeNetwork:
        raise NotImplementedError

    @abstractmethod
    def remove_network(self, *, network_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_machine(
        self,
        *,
        name: str,
        image: str,
        network_attachments: Sequence[RuntimeNetworkAttachment],
    ) -> RuntimeMachine:
        raise NotImplementedError

    @abstractmethod
    def start_machine(self, *, machine_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_machine(self, *, machine_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_machine(self, *, machine_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def inspect_machine(self, *, machine_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def inspect_network(self, *, network_id: str) -> dict:
        raise NotImplementedError
