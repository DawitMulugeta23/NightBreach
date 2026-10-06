"""Flag derivation, planting and checking. The backend is the only authority."""
from __future__ import annotations

import asyncio
import hashlib
import hmac
from typing import Any
from uuid import UUID

from .registry import FLAG_FOUND, LabObjective, get_lab

FLAG_SETTER = "/usr/local/sbin/nb-set-flag"

_PLANT_ATTEMPTS = 5
_RETRY_DELAY_SECONDS = 1.0
_EXEC_TIMEOUT_SECONDS = 15


class LabProvisioningError(RuntimeError):
    """A lab could not be prepared. Details are for server logs only."""


def derive_flag(*, secret: str, environment_id: UUID, objective: LabObjective) -> str:
    digest = hmac.new(
        secret.encode(),
        f"{environment_id}:{objective.id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"NB{{{objective.flag_prefix}_{digest[:16]}}}"


def check_flag(*, submission: str, expected: str) -> bool:
    return hmac.compare_digest(submission.strip().encode(), expected.encode())


async def _exec_with_retry(runtime: Any, machine_id: str, command: list[str], mask: str) -> None:
    last = "no attempt made"

    for attempt in range(_PLANT_ATTEMPTS):
        try:
            result = await asyncio.to_thread(
                runtime.execute_command,
                machine_id=machine_id,
                command=command,
                timeout=_EXEC_TIMEOUT_SECONDS,
            )
            if result.exit_code == 0:
                return
            last = f"exit {result.exit_code}: {(result.stderr or result.stdout).strip()}"
        except Exception as exc:  # runtime errors are retried, then reported
            last = str(exc)

        if attempt < _PLANT_ATTEMPTS - 1:
            await asyncio.sleep(_RETRY_DELAY_SECONDS)

    raise LabProvisioningError(
        f"Failed to plant flag after {_PLANT_ATTEMPTS} attempts: {last.replace(mask, '<flag>')}"
    )


async def plant_lab_flags(runtime: Any, environment: Any) -> None:
    """(Re)plant every flag objective of the environment's lab. Idempotent."""
    lab = get_lab(environment.lab_slug or "")

    if lab is None or not environment.lab_secret:
        raise LabProvisioningError("Environment is not a valid lab environment.")

    machines = {machine.name: machine for machine in environment.machines}

    for objective in lab.objectives:
        if objective.type != FLAG_FOUND:
            continue

        machine = machines.get(objective.machine)

        if machine is None or machine.runtime_machine_id is None:
            raise LabProvisioningError(
                f"Machine '{objective.machine}' is not available for objective '{objective.id}'."
            )

        flag = derive_flag(
            secret=environment.lab_secret,
            environment_id=environment.id,
            objective=objective,
        )

        await _exec_with_retry(
            runtime,
            machine.runtime_machine_id,
            [FLAG_SETTER, flag],
            mask=flag,
        )
