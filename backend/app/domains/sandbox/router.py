from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db_session
from app.models.user import User

from .api.schemas import (
    CreateEnvironmentRequest,
    EnvironmentResponse,
    EnvironmentValidationResponse,
    ProvisionEnvironmentRequest,
)
from .dependencies import get_runtime_provider
from .runtime.provider import RuntimeProvider
from .services.environment_service import (
    EnvironmentService,
    InterfaceSpec,
    MachineSpec,
    NetworkSpec,
    RouteSpec,
    ServiceSpec,
)

from .labs.router import router as labs_router


router = APIRouter(
    prefix="/sandbox",
    tags=["sandbox"],
)
router.include_router(labs_router)


@router.post(
    "/environments",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_environment(
    request: CreateEnvironmentRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> EnvironmentResponse:
    service = EnvironmentService(session=session)

    environment = await service.create_environment(
        learner_id=current_user.id,
        activity_id=request.activity_id,
    )

    return EnvironmentResponse.from_environment(environment)


@router.get(
    "/environments/{environment_id}",
    response_model=EnvironmentResponse,
)
async def get_environment(
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> EnvironmentResponse:
    service = EnvironmentService(session=session)

    environment = await service.get_environment(
        environment_id=environment_id,
        learner_id=current_user.id,
    )

    if environment is None:
        raise NotFoundError("Environment not found.")

    return EnvironmentResponse.from_environment(environment)


@router.post(
    "/environments/{environment_id}/provision",
    response_model=EnvironmentResponse,
)
async def provision_environment(
    environment_id: UUID,
    request: ProvisionEnvironmentRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> EnvironmentResponse:
    service = EnvironmentService(
        session=session,
        runtime=runtime,
    )

    networks = tuple(
        NetworkSpec(
            name=network.name,
            subnet=network.subnet,
            gateway=network.gateway,
        )
        for network in request.networks
    )

    machines = tuple(
        MachineSpec(
            name=machine.name,
            role=machine.role,
            image=machine.image,
            interfaces=tuple(
                InterfaceSpec(
                    name=interface.name,
                    network_name=interface.network_name,
                    address=interface.address,
                )
                for interface in machine.interfaces
            ),
            hostname=machine.hostname,
            routes=tuple(
                RouteSpec(
                    destination=route.destination,
                    gateway=route.gateway,
                    network_name=route.network_name,
                )
                for route in machine.routes
            ),
            services=tuple(
                ServiceSpec(
                    name=service.name,
                    port=service.port,
                    protocol=service.protocol,
                    required=service.required,
                )
                for service in machine.services
            ),
        )
        for machine in request.machines
    )

    environment = await service.provision_environment(
        environment_id=environment_id,
        learner_id=current_user.id,
        networks=networks,
        machines=machines,
    )

    return EnvironmentResponse.from_environment(environment)


@router.post(
    "/environments/{environment_id}/start",
    response_model=EnvironmentResponse,
)
async def start_environment(
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> EnvironmentResponse:
    service = EnvironmentService(
        session=session,
        runtime=runtime,
    )

    environment = await service.start_environment(
        environment_id=environment_id,
        learner_id=current_user.id,
    )

    return EnvironmentResponse.from_environment(environment)


@router.post(
    "/environments/{environment_id}/reset",
    response_model=EnvironmentResponse,
)
async def reset_environment(
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> EnvironmentResponse:
    service = EnvironmentService(
        session=session,
        runtime=runtime,
    )

    environment = await service.reset_environment(
        environment_id=environment_id,
        learner_id=current_user.id,
    )

    return EnvironmentResponse.from_environment(environment)


@router.post(
    "/environments/{environment_id}/stop",
    response_model=EnvironmentResponse,
)
async def stop_environment(
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> EnvironmentResponse:
    service = EnvironmentService(
        session=session,
        runtime=runtime,
    )

    environment = await service.stop_environment(
        environment_id=environment_id,
        learner_id=current_user.id,
    )

    return EnvironmentResponse.from_environment(environment)


@router.post(
    "/environments/{environment_id}/validate",
    response_model=EnvironmentValidationResponse,
)
async def validate_environment(
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> EnvironmentValidationResponse:
    service = EnvironmentService(
        session=session,
        runtime=runtime,
    )

    result = await service.validate_environment(
        environment_id=environment_id,
        learner_id=current_user.id,
    )

    return EnvironmentValidationResponse.from_result(
        environment_id=environment_id,
        result=result,
    )


@router.post(
    "/environments/{environment_id}/terminate",
    response_model=EnvironmentResponse,
)
async def terminate_environment(
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> EnvironmentResponse:
    service = EnvironmentService(
        session=session,
        runtime=runtime,
    )

    environment = await service.terminate_environment(
        environment_id=environment_id,
        learner_id=current_user.id,
    )

    return EnvironmentResponse.from_environment(environment)
