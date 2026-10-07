"""Trusted lab definitions.

The server is the only source of truth for what a lab contains. Clients send a
lab slug; images, roles, addresses, resource limits and objectives all come
from here. Never build a definition from request data.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.models.sandbox import MachineRole

from ..runtime.provider import DEFAULT_CAPABILITIES, RuntimeMachineLimits

LAB_NETWORK_NAME = "lab"
LAB_INTERFACE_NAME = "eth0"

# Each lab gets its own /24 out of 10.200.0.0/16.
LAB_POOL = "10.200"
LAB_POOL_FIRST = 1
LAB_POOL_LAST = 250

FLAG_FOUND = "FLAG_FOUND"


@dataclass(frozen=True)
class LabMachine:
    name: str
    title: str
    role: MachineRole
    image: str
    host_octet: int
    limits: RuntimeMachineLimits
    # False for machines the learner must discover (for example by scanning).
    reveal_address: bool = True
    # Target Build System artifact this machine runs. For TARGET machines the
    # runtime spec (image + required services) is resolved from the targets
    # registry; the Sandbox never builds target content itself.
    target_id: str | None = None


@dataclass(frozen=True)
class LabObjective:
    id: str
    type: str
    title: str
    description: str
    machine: str
    points: int
    flag_prefix: str = ""


@dataclass(frozen=True)
class LabDefinition:
    slug: str
    name: str
    description: str
    version: str
    machines: tuple[LabMachine, ...]
    objectives: tuple[LabObjective, ...]
    ttl_minutes: int = 120

    def objective(self, objective_id: str) -> LabObjective | None:
        for objective in self.objectives:
            if objective.id == objective_id:
                return objective
        return None


# Limits mirror what scripts/check_lab_images.py verified.
_ATTACKER_LIMITS = RuntimeMachineLimits()
_PERMISSIONS_TARGET_LIMITS = RuntimeMachineLimits(
    memory="256m",
    pids=128,
    capabilities=DEFAULT_CAPABILITIES + ("SYS_CHROOT",),
)

LINUX_FILE_PERMISSIONS = LabDefinition(
    slug="linux-file-permissions",
    name="Linux File Permissions",
    description=(
        "Investigate a Linux server from an attack machine, find a file with "
        "unsafe permissions, and demonstrate its security impact."
    ),
    version="1.0",
    machines=(
        LabMachine(
            name="attacker",
            title="Attack Machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attacker:1.0",
            host_octet=10,
            limits=_ATTACKER_LIMITS,
        ),
        LabMachine(
            name="target",
            title="Linux Permissions Target",
            role=MachineRole.TARGET,
            image="nightbreach/linux-permissions-target:1.0",
            host_octet=20,
            limits=_PERMISSIONS_TARGET_LIMITS,
            reveal_address=False,
            target_id="linux-permissions",
        ),
    ),
    objectives=(
        LabObjective(
            id="permissions-flag-001",
            type=FLAG_FOUND,
            title="Recover the exposed flag",
            description=(
                "Find the target on the lab network, identify the file whose "
                "permissions expose sensitive data, and submit the flag you recover."
            ),
            machine="target",
            points=100,
            flag_prefix="perm",
        ),
    ),
)

LINUX_PRACTICE = LabDefinition(
    slug="linux-practice",
    name="Linux Practice Machine",
    description="A private Linux terminal for trying the commands from the lessons.",
    version="1.0",
    machines=(
        LabMachine(
            name="attacker",
            title="Practice Machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attacker:1.0",
            host_octet=10,
            limits=_ATTACKER_LIMITS,
        ),
    ),
    objectives=(),
    ttl_minutes=60,
)

LABS: dict[str, LabDefinition] = {
    LINUX_FILE_PERMISSIONS.slug: LINUX_FILE_PERMISSIONS,
    LINUX_PRACTICE.slug: LINUX_PRACTICE,
}


def get_lab(slug: str) -> LabDefinition | None:
    return LABS.get(slug)


def list_labs() -> list[LabDefinition]:
    return list(LABS.values())


def allocate_lab_subnet(used_subnets: set[str]) -> tuple[int, str, str] | None:
    """Return (index, subnet, gateway) for the first free lab /24, or None."""
    for index in range(LAB_POOL_FIRST, LAB_POOL_LAST + 1):
        subnet = f"{LAB_POOL}.{index}.0/24"
        if subnet not in used_subnets:
            return index, subnet, f"{LAB_POOL}.{index}.1"
    return None


def machine_address(index: int, machine: LabMachine) -> str:
    return f"{LAB_POOL}.{index}.{machine.host_octet}"
