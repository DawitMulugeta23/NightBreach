from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.sandbox import EnvironmentState, MachineRole


class LabSummary(BaseModel):
    slug: str
    name: str
    description: str
    version: str


class LabMachineResponse(BaseModel):
    name: str
    title: str
    role: MachineRole
    # None for machines the learner has to discover.
    address: str | None = None


class LabObjectiveResponse(BaseModel):
    id: str
    title: str
    description: str
    points: int


class LabEnvironmentResponse(BaseModel):
    environment_id: UUID
    lab_slug: str
    lab_name: str
    state: EnvironmentState
    expires_at: datetime | None = None
    network_subnet: str | None = None
    machines: list[LabMachineResponse]
    objectives: list[LabObjectiveResponse]


class VerifyObjectiveRequest(BaseModel):
    submission: str = Field(min_length=1, max_length=200)


class VerifyObjectiveResponse(BaseModel):
    objective_id: str
    correct: bool
