"""Target runtime specifications consumed by the Sandbox.

Flow:

    Target Definition (activity/lab)
           ↓
    Target Build System (targets/ builds the image)
           ↓
    Target Artifact / Image
           ↓
    Target Runtime Specification  ← this module
           ↓
    Sandbox Runtime Adapter (domains/sandbox)
           ↓
    Docker Target Machine

The Sandbox decides WHERE a target exists (environment, networks, addresses,
routes). The Target Build System decides WHAT exists inside the target
(installed software, vulnerable state, challenge files, flags).

Nothing in this module — or anywhere else in the Sandbox — builds target
content. The Sandbox only consumes the runtime specification below: an image
reference plus the services the built image is expected to expose. Build-time
logic such as installing packages or planting challenge data lives with the
target definitions under ``targets/`` in the repository root, which produce
the images referenced here.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TargetServiceSpec:
    """A service the built target image must expose to be ready."""

    name: str
    port: int
    protocol: str = "tcp"
    required: bool = True


@dataclass(frozen=True)
class TargetRuntimeSpec:
    """Runtime-facing description of a built target artifact.

    This is the contract between the Target Build System and the Sandbox:
    the build system guarantees the image exposes ``services``; the Sandbox
    guarantees it starts, networks and validates the target.
    """

    target_id: str
    image: str
    services: tuple[TargetServiceSpec, ...] = ()


# Registry of built target artifacts. Entries are added here when a target
# build output is registered; images are built from the repository's
# ``targets/`` directory (and lab-images/) by the Target Build System.
TARGET_RUNTIME_SPECS: dict[str, TargetRuntimeSpec] = {
    "linux-permissions": TargetRuntimeSpec(
        target_id="linux-permissions",
        image="nightbreach/linux-permissions-target:1.0",
        services=(
            TargetServiceSpec(name="ssh", port=22, protocol="tcp"),
        ),
    ),
}


def get_target_runtime_spec(target_id: str) -> TargetRuntimeSpec | None:
    return TARGET_RUNTIME_SPECS.get(target_id)


def target_service_specs(target_id: str | None) -> tuple[TargetServiceSpec, ...]:
    if target_id is None:
        return ()

    spec = TARGET_RUNTIME_SPECS.get(target_id)

    return spec.services if spec is not None else ()
