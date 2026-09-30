from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import LearningRepository


class LearningService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = LearningRepository(session)

    async def list_learning_paths(self):
        return await self.repository.list_published_learning_paths()

    async def get_learning_path(self, learning_path_id: UUID):
        return await self.repository.get_published_learning_path(
            learning_path_id
        )

    async def get_module(self, module_id: UUID):
        return await self.repository.get_published_module(module_id)

    async def get_room(self, room_id: UUID):
        return await self.repository.get_published_room(room_id)

    async def get_lesson(self, lesson_id: UUID):
        lesson = await self.repository.get_published_lesson(lesson_id)

        if lesson is None:
            return None

        # A lesson can only expose practices that are themselves published.
        lesson.lesson_practices = [
            lesson_practice
            for lesson_practice in lesson.lesson_practices
            if lesson_practice.practice is not None
            and lesson_practice.practice.status.value == "PUBLISHED"
        ]

        return lesson
