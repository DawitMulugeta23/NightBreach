from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import (
    LearnerLessonProgress,
    LearnerLearningPathProgress,
    LearnerModuleProgress,
    LearnerRoomProgress,
)


class ProgressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_lesson_progress(
        self,
        *,
        learner_id: UUID,
        lesson_id: UUID,
    ) -> LearnerLessonProgress | None:
        result = await self.session.execute(
            select(LearnerLessonProgress).where(
                LearnerLessonProgress.learner_id == learner_id,
                LearnerLessonProgress.lesson_id == lesson_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_room_progress(
        self,
        *,
        learner_id: UUID,
        room_id: UUID,
    ) -> LearnerRoomProgress | None:
        result = await self.session.execute(
            select(LearnerRoomProgress).where(
                LearnerRoomProgress.learner_id == learner_id,
                LearnerRoomProgress.room_id == room_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_module_progress(
        self,
        *,
        learner_id: UUID,
        module_id: UUID,
    ) -> LearnerModuleProgress | None:
        result = await self.session.execute(
            select(LearnerModuleProgress).where(
                LearnerModuleProgress.learner_id == learner_id,
                LearnerModuleProgress.module_id == module_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_learning_path_progress(
        self,
        *,
        learner_id: UUID,
        learning_path_id: UUID,
    ) -> LearnerLearningPathProgress | None:
        result = await self.session.execute(
            select(LearnerLearningPathProgress).where(
                LearnerLearningPathProgress.learner_id == learner_id,
                LearnerLearningPathProgress.learning_path_id == learning_path_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_lesson_progress(
        self,
        *,
        learner_id: UUID,
        room_id: UUID | None = None,
    ) -> list[LearnerLessonProgress]:
        query = select(LearnerLessonProgress).where(
            LearnerLessonProgress.learner_id == learner_id
        )

        if room_id is not None:
            from app.models.lesson import Lesson

            query = query.join(
                Lesson,
                Lesson.id == LearnerLessonProgress.lesson_id,
            ).where(
                Lesson.room_id == room_id
            )

        query = query.order_by(LearnerLessonProgress.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_room_progress(
        self,
        *,
        learner_id: UUID,
        module_id: UUID | None = None,
    ) -> list[LearnerRoomProgress]:
        query = select(LearnerRoomProgress).where(
            LearnerRoomProgress.learner_id == learner_id
        )

        if module_id is not None:
            from app.models.room import Room

            query = query.join(
                Room,
                Room.id == LearnerRoomProgress.room_id,
            ).where(
                Room.module_id == module_id
            )

        query = query.order_by(LearnerRoomProgress.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_module_progress(
        self,
        *,
        learner_id: UUID,
        learning_path_id: UUID | None = None,
    ) -> list[LearnerModuleProgress]:
        query = select(LearnerModuleProgress).where(
            LearnerModuleProgress.learner_id == learner_id
        )

        if learning_path_id is not None:
            from app.models.module import Module

            query = query.join(
                Module,
                Module.id == LearnerModuleProgress.module_id,
            ).where(
                Module.learning_path_id == learning_path_id
            )

        query = query.order_by(LearnerModuleProgress.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_learning_path_progress(
        self,
        *,
        learner_id: UUID,
    ) -> list[LearnerLearningPathProgress]:
        result = await self.session.execute(
            select(LearnerLearningPathProgress)
            .where(
                LearnerLearningPathProgress.learner_id == learner_id
            )
            .order_by(LearnerLearningPathProgress.created_at)
        )
        return list(result.scalars().all())

    async def create_lesson_progress(
        self,
        progress: LearnerLessonProgress,
    ) -> LearnerLessonProgress:
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def create_room_progress(
        self,
        progress: LearnerRoomProgress,
    ) -> LearnerRoomProgress:
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def create_module_progress(
        self,
        progress: LearnerModuleProgress,
    ) -> LearnerModuleProgress:
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def create_learning_path_progress(
        self,
        progress: LearnerLearningPathProgress,
    ) -> LearnerLearningPathProgress:
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def commit(self) -> None:
        await self.session.commit()
