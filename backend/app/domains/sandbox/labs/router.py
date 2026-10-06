from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User

from ..dependencies import get_runtime_provider
from ..runtime.provider import RuntimeProvider
from .registry import list_labs
from .schemas import (
    LabEnvironmentResponse,
    LabSummary,
    VerifyObjectiveRequest,
    VerifyObjectiveResponse,
)
from .service import LabService, build_lab_response

router = APIRouter()


@router.get("/labs", response_model=list[LabSummary])
async def list_available_labs(
    current_user: User = Depends(get_current_user),
) -> list[LabSummary]:
    return [
        LabSummary(slug=lab.slug, name=lab.name, description=lab.description, version=lab.version)
        for lab in list_labs()
    ]


@router.post("/labs/{slug}/launch", response_model=LabEnvironmentResponse)
async def launch_lab(
    slug: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> LabEnvironmentResponse:
    service = LabService(session=session, runtime=runtime)
    environment = await service.launch(learner_id=current_user.id, slug=slug)
    return build_lab_response(environment)


@router.get("/environments/{environment_id}/lab", response_model=LabEnvironmentResponse)
async def get_lab_environment(
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> LabEnvironmentResponse:
    service = LabService(session=session, runtime=runtime)
    environment = await service.get_lab_environment(
        environment_id=environment_id, learner_id=current_user.id
    )
    return build_lab_response(environment)


@router.post(
    "/environments/{environment_id}/objectives/{objective_id}/verify",
    response_model=VerifyObjectiveResponse,
)
async def verify_objective(
    environment_id: UUID,
    objective_id: str,
    request: VerifyObjectiveRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> VerifyObjectiveResponse:
    service = LabService(session=session, runtime=runtime)
    correct = await service.verify_objective(
        environment_id=environment_id,
        learner_id=current_user.id,
        objective_id=objective_id,
        submission=request.submission,
    )
    return VerifyObjectiveResponse(objective_id=objective_id, correct=correct)
