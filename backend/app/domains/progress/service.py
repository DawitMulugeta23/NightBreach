from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.models.lesson import Lesson, LessonStatus
from app.models.lesson_practice import LessonPractice
from app.models.learning_path import LearningPath, LearningPathStatus
from app.models.module import Module, ModuleStatus
from app.models.practice import Practice, PracticeStatus
from app.models.practice_activity import PracticeActivity
from app.models.practice_attempt import PracticeAttempt
from app.models.progress import (
    LearnerLessonProgress,
    LearnerLearningPathProgress,
    LearnerModuleProgress,
    LearnerRoomProgress,
    ProgressStatus,
)
from app.models.room import Room, RoomStatus

from .repository import ProgressRepository


class ProgressService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProgressRepository(session)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    async def get_lesson_progress(
        self,
        *,
        learner_id: UUID,
        lesson_id: UUID,
    ) -> LearnerLessonProgress | None:
        lesson = await self._get_published_lesson(lesson_id)

        if lesson is None:
            raise NotFoundError("Lesson not found.")

        return await self.repository.get_lesson_progress(
            learner_id=learner_id,
            lesson_id=lesson_id,
        )

    async def get_room_progress(
        self,
        *,
        learner_id: UUID,
        room_id: UUID,
    ) -> LearnerRoomProgress | None:
        room = await self._get_published_room(room_id)

        if room is None:
            raise NotFoundError("Room not found.")

        return await self.repository.get_room_progress(
            learner_id=learner_id,
            room_id=room_id,
        )

    async def get_module_progress(
        self,
        *,
        learner_id: UUID,
        module_id: UUID,
    ) -> LearnerModuleProgress | None:
        module = await self._get_published_module(module_id)

        if module is None:
            raise NotFoundError("Module not found.")

        return await self.repository.get_module_progress(
            learner_id=learner_id,
            module_id=module_id,
        )

    async def get_learning_path_progress(
        self,
        *,
        learner_id: UUID,
        learning_path_id: UUID,
    ) -> LearnerLearningPathProgress | None:
        path = await self._get_published_learning_path(
            learning_path_id
        )

        if path is None:
            raise NotFoundError("Learning path not found.")

        return await self.repository.get_learning_path_progress(
            learner_id=learner_id,
            learning_path_id=learning_path_id,
        )

    async def record_lesson_completion(
        self,
        *,
        learner_id: UUID,
        lesson_id: UUID,
    ) -> LearnerLessonProgress:
        lesson = await self._get_published_lesson(lesson_id)

        if lesson is None:
            raise NotFoundError("Lesson not found.")

        required_activity_ids = await self._get_required_activity_ids(
            lesson_id
        )

        successful_activity_ids = await self._get_successful_activity_ids(
            learner_id=learner_id,
            activity_ids=required_activity_ids,
        )

        missing = required_activity_ids - successful_activity_ids

        if missing:
            raise ValidationError(
                "Lesson requirements are not yet completed.",
                details={
                    "missing_required_activity_ids": [
                        str(activity_id)
                        for activity_id in missing
                    ]
                },
            )

        now = self._now()

        progress = await self.repository.get_lesson_progress(
            learner_id=learner_id,
            lesson_id=lesson_id,
        )

        if progress is None:
            progress = LearnerLessonProgress(
                id=uuid4(),
                learner_id=learner_id,
                lesson_id=lesson_id,
                status=ProgressStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                last_activity_at=now,
            )
            await self.repository.create_lesson_progress(progress)
        else:
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = (
                progress.completed_at or now
            )
            progress.started_at = progress.started_at or now
            progress.last_activity_at = now

        await self._propagate_completion(
            learner_id=learner_id,
            lesson=lesson,
            now=now,
        )

        await self.repository.commit()

        return progress

    async def record_room_completion(
        self,
        *,
        learner_id: UUID,
        room_id: UUID,
    ) -> LearnerRoomProgress:
        room = await self._get_published_room(room_id)

        if room is None:
            raise NotFoundError("Room not found.")

        complete = await self._is_room_complete(
            learner_id=learner_id,
            room_id=room_id,
        )

        if not complete:
            raise ValidationError(
                "Room requirements are not yet completed."
            )

        now = self._now()

        progress = await self.repository.get_room_progress(
            learner_id=learner_id,
            room_id=room_id,
        )

        if progress is None:
            progress = LearnerRoomProgress(
                id=uuid4(),
                learner_id=learner_id,
                room_id=room_id,
                status=ProgressStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                last_activity_at=now,
            )
            await self.repository.create_room_progress(progress)
        else:
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = (
                progress.completed_at or now
            )
            progress.started_at = progress.started_at or now
            progress.last_activity_at = now

        module = await self._get_published_module(room.module_id)

        if module is not None:
            await self._propagate_module_completion(
                learner_id=learner_id,
                module=module,
                now=now,
            )

        await self.repository.commit()

        return progress

    async def record_module_completion(
        self,
        *,
        learner_id: UUID,
        module_id: UUID,
    ) -> LearnerModuleProgress:
        module = await self._get_published_module(module_id)

        if module is None:
            raise NotFoundError("Module not found.")

        complete = await self._is_module_complete(
            learner_id=learner_id,
            module_id=module_id,
        )

        if not complete:
            raise ValidationError(
                "Module requirements are not yet completed."
            )

        now = self._now()

        progress = await self.repository.get_module_progress(
            learner_id=learner_id,
            module_id=module_id,
        )

        if progress is None:
            progress = LearnerModuleProgress(
                id=uuid4(),
                learner_id=learner_id,
                module_id=module_id,
                status=ProgressStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                last_activity_at=now,
            )
            await self.repository.create_module_progress(progress)
        else:
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = (
                progress.completed_at or now
            )
            progress.started_at = progress.started_at or now
            progress.last_activity_at = now

        path = await self._get_published_learning_path(
            module.learning_path_id
        )

        if path is not None:
            await self._propagate_path_completion(
                learner_id=learner_id,
                path=path,
                now=now,
            )

        await self.repository.commit()

        return progress

    async def record_learning_path_completion(
        self,
        *,
        learner_id: UUID,
        learning_path_id: UUID,
    ) -> LearnerLearningPathProgress:
        path = await self._get_published_learning_path(
            learning_path_id
        )

        if path is None:
            raise NotFoundError("Learning path not found.")

        complete = await self._is_learning_path_complete(
            learner_id=learner_id,
            learning_path_id=learning_path_id,
        )

        if not complete:
            raise ValidationError(
                "Learning path requirements are not yet completed."
            )

        now = self._now()

        progress = await self.repository.get_learning_path_progress(
            learner_id=learner_id,
            learning_path_id=learning_path_id,
        )

        if progress is None:
            progress = LearnerLearningPathProgress(
                id=uuid4(),
                learner_id=learner_id,
                learning_path_id=learning_path_id,
                status=ProgressStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                last_activity_at=now,
            )
            await self.repository.create_learning_path_progress(progress)
        else:
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = (
                progress.completed_at or now
            )
            progress.started_at = progress.started_at or now
            progress.last_activity_at = now

        await self.repository.commit()

        return progress

    async def _propagate_completion(
        self,
        *,
        learner_id: UUID,
        lesson: Lesson,
        now: datetime,
    ) -> None:
        room_complete = await self._is_room_complete(
            learner_id=learner_id,
            room_id=lesson.room_id,
        )

        if not room_complete:
            return

        room_progress = await self.repository.get_room_progress(
            learner_id=learner_id,
            room_id=lesson.room_id,
        )

        if room_progress is None:
            room_progress = LearnerRoomProgress(
                id=uuid4(),
                learner_id=learner_id,
                room_id=lesson.room_id,
                status=ProgressStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                last_activity_at=now,
            )
            await self.repository.create_room_progress(room_progress)
        else:
            room_progress.status = ProgressStatus.COMPLETED
            room_progress.completed_at = (
                room_progress.completed_at or now
            )
            room_progress.started_at = room_progress.started_at or now
            room_progress.last_activity_at = now

        room = await self._get_published_room(lesson.room_id)

        if room is None:
            return

        module = await self._get_published_module(room.module_id)

        if module is not None:
            await self._propagate_module_completion(
                learner_id=learner_id,
                module=module,
                now=now,
            )

    async def _propagate_module_completion(
        self,
        *,
        learner_id: UUID,
        module: Module,
        now: datetime,
    ) -> None:
        complete = await self._is_module_complete(
            learner_id=learner_id,
            module_id=module.id,
        )

        if not complete:
            return

        progress = await self.repository.get_module_progress(
            learner_id=learner_id,
            module_id=module.id,
        )

        if progress is None:
            progress = LearnerModuleProgress(
                id=uuid4(),
                learner_id=learner_id,
                module_id=module.id,
                status=ProgressStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                last_activity_at=now,
            )
            await self.repository.create_module_progress(progress)
        else:
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = (
                progress.completed_at or now
            )
            progress.started_at = progress.started_at or now
            progress.last_activity_at = now

        path = await self._get_published_learning_path(
            module.learning_path_id
        )

        if path is not None:
            await self._propagate_path_completion(
                learner_id=learner_id,
                path=path,
                now=now,
            )

    async def _propagate_path_completion(
        self,
        *,
        learner_id: UUID,
        path: LearningPath,
        now: datetime,
    ) -> None:
        complete = await self._is_learning_path_complete(
            learner_id=learner_id,
            learning_path_id=path.id,
        )

        if not complete:
            return

        progress = await self.repository.get_learning_path_progress(
            learner_id=learner_id,
            learning_path_id=path.id,
        )

        if progress is None:
            progress = LearnerLearningPathProgress(
                id=uuid4(),
                learner_id=learner_id,
                learning_path_id=path.id,
                status=ProgressStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                last_activity_at=now,
            )
            await self.repository.create_learning_path_progress(progress)
        else:
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = (
                progress.completed_at or now
            )
            progress.started_at = progress.started_at or now
            progress.last_activity_at = now

    async def _get_required_activity_ids(
        self,
        lesson_id: UUID,
    ) -> set[UUID]:
        result = await self.session.execute(
            select(PracticeActivity.id)
            .join(
                LessonPractice,
                LessonPractice.practice_id
                == PracticeActivity.practice_id,
            )
            .join(
                Practice,
                Practice.id == LessonPractice.practice_id,
            )
            .where(
                LessonPractice.lesson_id == lesson_id,
                Practice.status == PracticeStatus.PUBLISHED,
                PracticeActivity.required.is_(True),
            )
        )

        return set(result.scalars().all())

    async def _get_successful_activity_ids(
        self,
        *,
        learner_id: UUID,
        activity_ids: set[UUID],
    ) -> set[UUID]:
        if not activity_ids:
            return set()

        result = await self.session.execute(
            select(PracticeAttempt.practice_activity_id)
            .where(
                PracticeAttempt.learner_id == learner_id,
                PracticeAttempt.practice_activity_id.in_(activity_ids),
                PracticeAttempt.result == "SUCCESS",
            )
            .distinct()
        )

        return set(result.scalars().all())

    async def _is_room_complete(
        self,
        *,
        learner_id: UUID,
        room_id: UUID,
    ) -> bool:
        lesson_ids_result = await self.session.execute(
            select(Lesson.id).where(
                Lesson.room_id == room_id,
                Lesson.status == LessonStatus.PUBLISHED,
            )
        )

        lesson_ids = list(lesson_ids_result.scalars().all())

        if not lesson_ids:
            return False

        completed_result = await self.session.execute(
            select(func.count(LearnerLessonProgress.id))
            .where(
                LearnerLessonProgress.learner_id == learner_id,
                LearnerLessonProgress.lesson_id.in_(lesson_ids),
                LearnerLessonProgress.status
                == ProgressStatus.COMPLETED,
            )
        )

        completed_count = completed_result.scalar_one()

        return completed_count == len(lesson_ids)

    async def _is_module_complete(
        self,
        *,
        learner_id: UUID,
        module_id: UUID,
    ) -> bool:
        room_ids_result = await self.session.execute(
            select(Room.id).where(
                Room.module_id == module_id,
                Room.status == RoomStatus.PUBLISHED,
            )
        )

        room_ids = list(room_ids_result.scalars().all())

        if not room_ids:
            return False

        completed_result = await self.session.execute(
            select(func.count(LearnerRoomProgress.id))
            .where(
                LearnerRoomProgress.learner_id == learner_id,
                LearnerRoomProgress.room_id.in_(room_ids),
                LearnerRoomProgress.status
                == ProgressStatus.COMPLETED,
            )
        )

        completed_count = completed_result.scalar_one()

        return completed_count == len(room_ids)

    async def _is_learning_path_complete(
        self,
        *,
        learner_id: UUID,
        learning_path_id: UUID,
    ) -> bool:
        module_ids_result = await self.session.execute(
            select(Module.id).where(
                Module.learning_path_id == learning_path_id,
                Module.status == ModuleStatus.PUBLISHED,
            )
        )

        module_ids = list(module_ids_result.scalars().all())

        if not module_ids:
            return False

        completed_result = await self.session.execute(
            select(func.count(LearnerModuleProgress.id))
            .where(
                LearnerModuleProgress.learner_id == learner_id,
                LearnerModuleProgress.module_id.in_(module_ids),
                LearnerModuleProgress.status
                == ProgressStatus.COMPLETED,
            )
        )

        completed_count = completed_result.scalar_one()

        return completed_count == len(module_ids)

    async def _get_published_lesson(
        self,
        lesson_id: UUID,
    ) -> Lesson | None:
        result = await self.session.execute(
            select(Lesson).where(
                Lesson.id == lesson_id,
                Lesson.status == LessonStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def _get_published_room(
        self,
        room_id: UUID,
    ) -> Room | None:
        result = await self.session.execute(
            select(Room).where(
                Room.id == room_id,
                Room.status == RoomStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def _get_published_module(
        self,
        module_id: UUID,
    ) -> Module | None:
        result = await self.session.execute(
            select(Module).where(
                Module.id == module_id,
                Module.status == ModuleStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def _get_published_learning_path(
        self,
        learning_path_id: UUID,
    ) -> LearningPath | None:
        result = await self.session.execute(
            select(LearningPath).where(
                LearningPath.id == learning_path_id,
                LearningPath.status == LearningPathStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def list_completed_rooms(
        self,
        *,
        learner_id: UUID,
        module_id: UUID | None = None,
    ) -> list[LearnerRoomProgress]:
        progress_records = await self.repository.list_room_progress(
            learner_id=learner_id,
            module_id=module_id,
        )

        return [
            progress
            for progress in progress_records
            if progress.status == ProgressStatus.COMPLETED
        ]

    async def list_completed_modules(
        self,
        *,
        learner_id: UUID,
        learning_path_id: UUID | None = None,
    ) -> list[LearnerModuleProgress]:
        progress_records = await self.repository.list_module_progress(
            learner_id=learner_id,
            learning_path_id=learning_path_id,
        )

        return [
            progress
            for progress in progress_records
            if progress.status == ProgressStatus.COMPLETED
        ]

    async def get_completion_state(
        self,
        *,
        learner_id: UUID,
        lesson_id: UUID,
    ) -> dict[str, UUID | ProgressStatus]:
        lesson = await self._get_published_lesson(lesson_id)

        if lesson is None:
            raise NotFoundError("Lesson not found.")

        room = await self._get_published_room(lesson.room_id)

        if room is None:
            raise NotFoundError("Room not found.")

        module = await self._get_published_module(room.module_id)

        if module is None:
            raise NotFoundError("Module not found.")

        path = await self._get_published_learning_path(
            module.learning_path_id
        )

        if path is None:
            raise NotFoundError("Learning path not found.")

        lesson_progress = await self.repository.get_lesson_progress(
            learner_id=learner_id,
            lesson_id=lesson.id,
        )

        room_progress = await self.repository.get_room_progress(
            learner_id=learner_id,
            room_id=room.id,
        )

        module_progress = await self.repository.get_module_progress(
            learner_id=learner_id,
            module_id=module.id,
        )

        path_progress = await self.repository.get_learning_path_progress(
            learner_id=learner_id,
            learning_path_id=path.id,
        )

        return {
            "lesson_id": lesson.id,
            "room_id": room.id,
            "module_id": module.id,
            "learning_path_id": path.id,
            "lesson_status": (
                lesson_progress.status
                if lesson_progress is not None
                else ProgressStatus.NOT_STARTED
            ),
            "room_status": (
                room_progress.status
                if room_progress is not None
                else ProgressStatus.NOT_STARTED
            ),
            "module_status": (
                module_progress.status
                if module_progress is not None
                else ProgressStatus.NOT_STARTED
            ),
            "learning_path_status": (
                path_progress.status
                if path_progress is not None
                else ProgressStatus.NOT_STARTED
            ),
        }

    async def process_successful_activity(
        self,
        *,
        learner_id: UUID,
        activity_id: UUID,
    ) -> None:
        """
        Re-evaluate published Lessons associated with a successfully
        completed Practice activity.

        A successful required activity starts lesson progress when needed.
        The lesson becomes COMPLETED only after every required activity
        succeeds.

        This method does not commit. The caller owns the transaction.
        """
        lesson_ids_result = await self.session.execute(
            select(LessonPractice.lesson_id)
            .join(
                Practice,
                Practice.id == LessonPractice.practice_id,
            )
            .join(
                PracticeActivity,
                PracticeActivity.practice_id == Practice.id,
            )
            .where(
                PracticeActivity.id == activity_id,
                Practice.status == PracticeStatus.PUBLISHED,
            )
            .distinct()
        )

        lesson_ids = list(lesson_ids_result.scalars().all())

        if not lesson_ids:
            return

        now = self._now()

        for lesson_id in lesson_ids:
            lesson = await self._get_published_lesson(lesson_id)

            if lesson is None:
                continue

            required_activity_ids = await self._get_required_activity_ids(
                lesson_id
            )

            successful_activity_ids = (
                await self._get_successful_activity_ids(
                    learner_id=learner_id,
                    activity_ids=required_activity_ids,
                )
            )

            progress = await self.repository.get_lesson_progress(
                learner_id=learner_id,
                lesson_id=lesson.id,
            )

            all_requirements_completed = (
                not required_activity_ids - successful_activity_ids
            )

            if progress is None:
                progress = LearnerLessonProgress(
                    id=uuid4(),
                    learner_id=learner_id,
                    lesson_id=lesson.id,
                    status=(
                        ProgressStatus.COMPLETED
                        if all_requirements_completed
                        else ProgressStatus.IN_PROGRESS
                    ),
                    started_at=now,
                    completed_at=(
                        now if all_requirements_completed else None
                    ),
                    last_activity_at=now,
                )
                await self.repository.create_lesson_progress(progress)
            else:
                progress.started_at = progress.started_at or now
                progress.last_activity_at = now

                if all_requirements_completed:
                    progress.status = ProgressStatus.COMPLETED
                    progress.completed_at = (
                        progress.completed_at or now
                    )
                elif progress.status != ProgressStatus.COMPLETED:
                    progress.status = ProgressStatus.IN_PROGRESS

            if all_requirements_completed:
                await self._propagate_completion(
                    learner_id=learner_id,
                    lesson=lesson,
                    now=now,
                )
