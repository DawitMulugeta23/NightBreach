"""Binds lab-backed CTF challenges to sandbox lab environments.

A challenge opts in with
    validation_config = {"lab": {"slug": ..., "objective_id": ...}}
The CTF domain only sees the resolver interface it declares; this module is the
implementation, so the CTF domain never imports sandbox internals.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.models.sandbox import EnvironmentState

from ..repositories.environment_repository import EnvironmentRepository
from .flags import derive_flag
from .registry import FLAG_FOUND, get_lab

_RUNNING = (EnvironmentState.READY, EnvironmentState.ACTIVE)


class LabChallengeConfigurationError(RuntimeError):
    """A lab-backed challenge references a lab or objective that does not exist."""


class LabChallengeResolver:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = EnvironmentRepository(session)

    @staticmethod
    def _objective(lab_reference: dict[str, Any]):
        slug = lab_reference.get("slug")
        objective_id = lab_reference.get("objective_id")

        lab = get_lab(slug) if isinstance(slug, str) else None
        objective = (
            lab.objective(objective_id)
            if lab is not None and isinstance(objective_id, str)
            else None
        )

        if objective is None or objective.type != FLAG_FOUND:
            raise LabChallengeConfigurationError(
                "Lab challenge references an unknown lab or flag objective."
            )

        return slug, objective

    async def _running_environment(
        self,
        *,
        learner_id: UUID,
        environment_id: UUID | None,
        slug: str,
    ):
        if environment_id is None:
            raise ConflictError("Launch the lab before starting this challenge.")

        # Scoped to the learner: someone else's environment looks like a missing one.
        environment = await self.repository.get_for_learner(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment is None or environment.lab_slug != slug:
            raise NotFoundError("Lab environment not found.")

        if environment.state not in _RUNNING:
            raise ConflictError("The lab environment is not running.")

        return environment

    async def check_attempt_start(
        self,
        *,
        learner_id: UUID,
        environment_id: UUID | None,
        lab_reference: dict[str, Any],
    ) -> None:
        slug, _ = self._objective(lab_reference)
        await self._running_environment(
            learner_id=learner_id,
            environment_id=environment_id,
            slug=slug,
        )

    async def expected_flag(
        self,
        *,
        learner_id: UUID,
        environment_id: UUID | None,
        lab_reference: dict[str, Any],
    ) -> str:
        slug, objective = self._objective(lab_reference)
        environment = await self._running_environment(
            learner_id=learner_id,
            environment_id=environment_id,
            slug=slug,
        )

        if not environment.lab_secret:
            raise LabChallengeConfigurationError("Lab environment has no flag secret.")

        return derive_flag(
            secret=environment.lab_secret,
            environment_id=environment.id,
            objective=objective,
        )
