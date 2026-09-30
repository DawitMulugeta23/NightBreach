from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.sandbox import EnvironmentState, MachineRole


class CreateEnvironmentRequest(BaseModel):
    activity_id: str = Field(min_length=1, max_length=255)


class InterfaceSpecRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    network_name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=64)


class NetworkSpecRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    subnet: str = Field(min_length=1, max_length=64)
    gateway: str = Field(min_length=1, max_length=64)


class MachineSpecRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    role: MachineRole
    image: str = Field(min_length=1, max_length=500)
    interfaces: list[InterfaceSpecRequest] = Field(min_length=1)


class ProvisionEnvironmentRequest(BaseModel):
    networks: list[NetworkSpecRequest] = Field(min_length=1)
    machines: list[MachineSpecRequest] = Field(min_length=1)


class EnvironmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learner_id: UUID
    activity_id: str
    state: EnvironmentState
    state_version: int


class EnvironmentValidationResponse(BaseModel):
    environment_id: UUID
    valid: bool
    errors: list[str] = Field(default_factory=list)
