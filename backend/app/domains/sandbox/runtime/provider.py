from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence


DEFAULT_CAPABILITIES: tuple[str, ...] = (
    "CHOWN",
    "DAC_OVERRIDE",
    "FOWNER",
    "SETGID",
    "SETUID",
    "KILL",
    "NET_BIND_SERVICE",
    "NET_RAW",
)


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


@dataclass(frozen=True)
class RuntimeCommandResult:
    exit_code: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class RuntimeMachineLimits:
    """Resource and privilege limits applied to every sandbox machine."""

    memory: str = "512m"
    cpus: float = 1.0
    pids: int = 256
    capabilities: tuple[str, ...] = DEFAULT_CAPABILITIES
    # Must be False only for deliberately vulnerable SUID targets.
    no_new_privileges: bool = True
    read_only_rootfs: bool = False
    user: str | None = None


class RuntimeShell(ABC):
    """An interactive shell (TTY with stdin/stdout) attached to a machine."""

    @abstractmethod
    def read(self) -> bytes | None:
        """Block until output is available. None means the shell has ended."""
        raise NotImplementedError

    @abstractmethod
    def write(self, data: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    def resize(self, cols: int, rows: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class RuntimeProvider(ABC):
    """Logical runtime interface owned by the Sandbox domain."""

    @abstractmethod
    def create_network(
        self,
        *,
        name: str,
        subnet: str | None = None,
        gateway: str | None = None,
        internal: bool = True,
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
        limits: RuntimeMachineLimits | None = None,
        command: Sequence[str] | None = None,
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

    @abstractmethod
    def execute_command(
        self,
        *,
        machine_id: str,
        command: Sequence[str],
        timeout: int | None = None,
    ) -> RuntimeCommandResult:
        raise NotImplementedError

    def open_shell(
        self,
        *,
        machine_id: str,
        command: Sequence[str] = ("/bin/bash", "-i"),
        environment: dict[str, str] | None = None,
    ) -> RuntimeShell:
        """Open an interactive shell. Providers that cannot do this raise."""
        raise NotImplementedError
