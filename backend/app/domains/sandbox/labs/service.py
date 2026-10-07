from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.models.sandbox import Environment, EnvironmentState

from ..runtime.provider import RuntimeProvider
from ..services.environment_service import (
    EnvironmentProvisioningError,
    EnvironmentService,
    InterfaceSpec,
    MachineSpec,
    NetworkSpec,
    SandboxServiceError,
    ServiceSpec,
)
from ..targets import target_service_specs
from .flags import FLAG_FOUND, check_flag, derive_flag, plant_lab_flags
from .registry import (
    LAB_INTERFACE_NAME,
    LAB_NETWORK_NAME,
    LabDefinition,
    allocate_lab_subnet,
    get_lab,
    machine_address,
)
from .schemas import (
    LabEnvironmentResponse,
    LabMachineResponse,
    LabObjectiveResponse,
)


def build_lab_response(environment: Environment) -> LabEnvironmentResponse:
    lab = get_lab(environment.lab_slug or "")

    if lab is None:
        raise NotFoundError("This environment is not a lab.")

    addresses = {
        machine.name: (machine.interfaces[0].address if machine.interfaces else None)
        for machine in environment.machines
    }

    return LabEnvironmentResponse(
        environment_id=environment.id,
        lab_slug=lab.slug,
        lab_name=lab.name,
        state=environment.state,
        expires_at=environment.expires_at,
        network_subnet=environment.networks[0].subnet if environment.networks else None,
        machines=[
            LabMachineResponse(
                name=machine.name,
                title=machine.title,
                role=machine.role,
                address=addresses.get(machine.name) if machine.reveal_address else None,
            )
            for machine in lab.machines
        ],
        objectives=[
            LabObjectiveResponse(
                id=objective.id,
                title=objective.title,
                description=objective.description,
                points=objective.points,
            )
            for objective in lab.objectives
        ],
    )


class LabService:
    """Launches and verifies lab environments from the trusted registry."""

    def __init__(self, *, session: AsyncSession, runtime: RuntimeProvider) -> None:
        self.runtime = runtime
        self.environments = EnvironmentService(session=session, runtime=runtime)
        self.repository = self.environments.repository

    async def launch(self, *, learner_id: UUID, slug: str) -> Environment:
        lab = get_lab(slug)

        if lab is None:
            raise NotFoundError("Lab not found.")

        now = datetime.now(timezone.utc)

        for live in await self.repository.list_live_lab_environments(learner_id=learner_id):
            if live.expires_at is not None and live.expires_at <= now:
                try:
                    await self.environments.terminate_environment(
                        environment_id=live.id, learner_id=learner_id
                    )
                except Exception:
                    pass
                continue

            if live.lab_slug != slug:
                raise ConflictError(
                    "Finish or terminate your active lab before launching another one."
                )

            if live.state == EnvironmentState.STOPPED:
                await self.environments.start_environment(
                    environment_id=live.id, learner_id=learner_id
                )
            elif live.state not in (EnvironmentState.READY, EnvironmentState.ACTIVE):
                raise ConflictError("This lab is still starting. Try again in a moment.")

            return await self.environments.get_environment(
                environment_id=live.id, learner_id=learner_id
            )

        return await self._create_and_provision(learner_id=learner_id, lab=lab, now=now)

    async def _create_and_provision(
        self, *, learner_id: UUID, lab: LabDefinition, now: datetime
    ) -> Environment:
        allocation = allocate_lab_subnet(await self.repository.list_allocated_subnets())

        if allocation is None:
            raise ConflictError("No lab capacity is available right now. Try again later.")

        index, subnet, gateway = allocation

        created = await self.repository.create(
            Environment(
                learner_id=learner_id,
                activity_id=f"lab:{lab.slug}",
                state=EnvironmentState.REQUESTED,
                state_version=1,
                lab_slug=lab.slug,
                lab_secret=secrets.token_hex(16),
                expires_at=now + timedelta(minutes=lab.ttl_minutes),
            )
        )
        await self.repository.commit()
        environment_id = created.id

        try:
            await self.environments.provision_environment(
                environment_id=environment_id,
                learner_id=learner_id,
                networks=(NetworkSpec(name=LAB_NETWORK_NAME, subnet=subnet, gateway=gateway),),
                machines=tuple(
                    MachineSpec(
                        name=machine.name,
                        role=machine.role,
                        image=machine.image,
                        interfaces=(
                            InterfaceSpec(
                                name=LAB_INTERFACE_NAME,
                                network_name=LAB_NETWORK_NAME,
                                address=machine_address(index, machine),
                            ),
                        ),
                        limits=machine.limits,
                        # Services come from the Target Build System's
                        # runtime spec; the Sandbox only validates them.
                        services=tuple(
                            ServiceSpec(
                                name=service.name,
                                port=service.port,
                                protocol=service.protocol,
                                required=service.required,
                            )
                            for service in target_service_specs(
                                machine.target_id
                            )
                        ),
                    )
                    for machine in lab.machines
                ),
            )

            environment = await self.environments.get_environment(
                environment_id=environment_id, learner_id=learner_id
            )
            await plant_lab_flags(self.runtime, environment)

            health = await self.environments.validate_environment(
                environment_id=environment_id, learner_id=learner_id
            )
            if not health.valid:
                raise EnvironmentProvisioningError("Lab failed its health check.")

            return await self.environments.get_environment(
                environment_id=environment_id, learner_id=learner_id
            )

        except Exception as exc:
            try:
                await self.environments.terminate_environment(
                    environment_id=environment_id, learner_id=learner_id
                )
            except Exception:
                pass

            if isinstance(exc, SandboxServiceError):
                raise

            raise EnvironmentProvisioningError("The lab could not be prepared.") from exc

    async def get_lab_environment(
        self, *, environment_id: UUID, learner_id: UUID
    ) -> Environment:
        environment = await self.environments.get_environment(
            environment_id=environment_id, learner_id=learner_id
        )

        if environment.lab_slug is None:
            raise NotFoundError("This environment is not a lab.")

        return environment

    async def verify_objective(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
        objective_id: str,
        submission: str,
    ) -> bool:
        environment = await self.get_lab_environment(
            environment_id=environment_id, learner_id=learner_id
        )

        if environment.state not in (EnvironmentState.READY, EnvironmentState.ACTIVE):
            raise ConflictError("The lab environment is not running.")

        lab = get_lab(environment.lab_slug or "")
        objective = lab.objective(objective_id) if lab else None

        if objective is None or not environment.lab_secret:
            raise NotFoundError("Objective not found.")

        if objective.type == FLAG_FOUND:
            expected = derive_flag(
                secret=environment.lab_secret,
                environment_id=environment.id,
                objective=objective,
            )
            return check_flag(submission=submission, expected=expected)

        raise ConflictError("This objective type cannot be verified yet.")
