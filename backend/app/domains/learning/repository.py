from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lesson import Lesson, LessonStatus
from app.models.lesson_practice import LessonPractice
from app.models.learning_path import LearningPath, LearningPathStatus
from app.models.module import Module, ModuleStatus
from app.models.practice import Practice, PracticeStatus
from app.models.practice_activity import PracticeActivity
from app.models.room import Room, RoomStatus


class LearningRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_published_learning_paths(self) -> list[LearningPath]:
        result = await self.session.execute(
            select(LearningPath)
            .where(LearningPath.status == LearningPathStatus.PUBLISHED)
            .order_by(LearningPath.position)
        )

        return list(result.scalars().all())

    async def get_published_learning_path(
        self,
        learning_path_id: UUID,
    ) -> LearningPath | None:
        result = await self.session.execute(
            select(LearningPath)
            .options(
                selectinload(
                    LearningPath.modules.and_(
                        Module.status == ModuleStatus.PUBLISHED
                    )
                )
            )
            .where(
                LearningPath.id == learning_path_id,
                LearningPath.status == LearningPathStatus.PUBLISHED,
            )
        )

        return result.scalar_one_or_none()

    async def get_published_module(
        self,
        module_id: UUID,
    ) -> Module | None:
        result = await self.session.execute(
            select(Module)
            .options(
                selectinload(
                    Module.rooms.and_(
                        Room.status == RoomStatus.PUBLISHED
                    )
                )
            )
            .join(Module.learning_path)
            .where(
                Module.id == module_id,
                Module.status == ModuleStatus.PUBLISHED,
                LearningPath.status == LearningPathStatus.PUBLISHED,
            )
        )

        return result.scalar_one_or_none()

    async def get_published_room(
        self,
        room_id: UUID,
    ) -> Room | None:
        result = await self.session.execute(
            select(Room)
            .options(
                selectinload(
                    Room.lessons.and_(
                        Lesson.status == LessonStatus.PUBLISHED
                    )
                )
            )
            .join(Room.module)
            .join(Module.learning_path)
            .where(
                Room.id == room_id,
                Room.status == RoomStatus.PUBLISHED,
                Module.status == ModuleStatus.PUBLISHED,
                LearningPath.status == LearningPathStatus.PUBLISHED,
            )
        )

        return result.scalar_one_or_none()

    async def get_published_lesson(
        self,
        lesson_id: UUID,
    ) -> Lesson | None:
        result = await self.session.execute(
            select(Lesson)
            .options(
                selectinload(Lesson.content_blocks),
                selectinload(Lesson.lesson_practices)
                .selectinload(LessonPractice.practice)
                .selectinload(Practice.activities),
            )
            .join(Lesson.room)
            .join(Room.module)
            .join(Module.learning_path)
            .where(
                Lesson.id == lesson_id,
                Lesson.status == LessonStatus.PUBLISHED,
                Room.status == RoomStatus.PUBLISHED,
                Module.status == ModuleStatus.PUBLISHED,
                LearningPath.status == LearningPathStatus.PUBLISHED,
            )
        )

        return result.scalar_one_or_none()

    async def get_published_practice(
        self,
        practice_id: UUID,
    ) -> Practice | None:
        result = await self.session.execute(
            select(Practice)
            .options(
                selectinload(Practice.activities)
            )
            .where(
                Practice.id == practice_id,
                Practice.status == PracticeStatus.PUBLISHED,
            )
        )

        return result.scalar_one_or_none()
