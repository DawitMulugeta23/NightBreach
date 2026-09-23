import hashlib

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.session import get_db
from db.models import (
    LearningPath, Room, Lesson, LessonQuestion, QuestionType,
    UserQuestionProgress, UserLessonProgress, UserWrongAttempt, User, ContainerStatus,
)
from core.security import get_current_user_id
from core.onboarding_quiz import UPGRADE_THRESHOLD, UPGRADE_WINDOW
from orchestrator.session_manager import get_or_create_session
from orchestrator.provisioning import provision_container
from orchestrator.terminal import get_docker_client

_docker_client = get_docker_client()

router = APIRouter(prefix="/learning", tags=["learning"])

FOUNDATION_SLUGS = {"linux-fundamentals", "networking-fundamentals", "fundamental-cybersecurity"}


async def _is_path_completed(db: AsyncSession, user_id, path_id) -> bool:
    """True if every lesson in every room of this path is completed by this user."""
    result = await db.execute(
        select(Lesson.id).join(Room, Room.id == Lesson.room_id).where(Room.path_id == path_id)
    )
    lesson_ids = {row[0] for row in result.all()}
    if not lesson_ids:
        return False
    result = await db.execute(
        select(UserLessonProgress.lesson_id)
        .where(UserLessonProgress.user_id == user_id)
        .where(UserLessonProgress.lesson_id.in_(lesson_ids))
    )
    completed_ids = {row[0] for row in result.all()}
    return lesson_ids.issubset(completed_ids)


async def _is_room_completed(db: AsyncSession, user_id, room) -> bool:
    """True if every lesson in this room is completed by this user."""
    result = await db.execute(select(Lesson.id).where(Lesson.room_id == room.id))
    lesson_ids = {row[0] for row in result.all()}
    if not lesson_ids:
        return False
    result = await db.execute(
        select(UserLessonProgress.lesson_id)
        .where(UserLessonProgress.user_id == user_id)
        .where(UserLessonProgress.lesson_id.in_(lesson_ids))
    )
    completed_ids = {row[0] for row in result.all()}
    return lesson_ids.issubset(completed_ids)


def _hash_answer(answer: str) -> str:
    return hashlib.sha256(answer.strip().lower().encode()).hexdigest()


# ---- Response models ----
class PathSummary(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    icon: str | None
    order_index: int
    room_count: int
    tier: str
    locked: bool
    completed: bool


class RoomSummary(BaseModel):
    id: str
    title: str
    description: str
    order_index: int
    lesson_count: int
    locked: bool


class PathDetail(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    icon: str | None
    rooms: list[RoomSummary]


class LessonSummary(BaseModel):
    id: str
    title: str
    order_index: int
    completed: bool


class QuestionDetail(BaseModel):
    id: str
    order_index: int
    question_type: str
    difficulty: str
    prompt: str
    answered: bool


class LessonDetail(BaseModel):
    id: str
    title: str
    order_index: int
    blocks: list[dict]
    questions: list[QuestionDetail]
    completed: bool
    prev_lesson_id: str | None
    next_lesson_id: str | None


class AnswerSubmission(BaseModel):
    answer: str


# ---- Endpoints ----

@router.get("/paths", response_model=list[PathSummary])
async def list_paths(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LearningPath).options(selectinload(LearningPath.rooms)).order_by(LearningPath.order_index)
    )
    paths = result.scalars().all()

    foundations_done = True
    path_completed = {}
    for p in paths:
        if p.slug in FOUNDATION_SLUGS:
            done = await _is_path_completed(db, user_id, p.id)
            path_completed[p.id] = done
            if not done:
                foundations_done = False
        else:
            path_completed[p.id] = False

    return [
        PathSummary(
            id=str(p.id), slug=p.slug, title=p.title, description=p.description,
            icon=p.icon, order_index=p.order_index, room_count=len(p.rooms),
            tier=("foundations" if p.slug in FOUNDATION_SLUGS else "specializations"),
            locked=(p.slug not in FOUNDATION_SLUGS and not foundations_done),
            completed=path_completed[p.id],
        )
        for p in paths
    ]


@router.get("/paths/{path_id}", response_model=PathDetail)
async def get_path(path_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LearningPath)
        .options(selectinload(LearningPath.rooms).selectinload(Room.lessons))
        .where(LearningPath.id == path_id)
    )
    path = result.scalar_one_or_none()
    if path is None:
        raise HTTPException(status_code=404, detail="Path not found")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    free_mode = user is not None and user.progression_mode == "free"

    sorted_rooms = sorted(path.rooms, key=lambda r: r.order_index)

    rooms = []
    prev_completed = True  # room at order_index 1 is always unlocked
    for r in sorted_rooms:
        if free_mode:
            locked = False
        else:
            locked = not prev_completed
        rooms.append(RoomSummary(
            id=str(r.id), title=r.title, description=r.description,
            order_index=r.order_index, lesson_count=len(r.lessons),
            locked=locked,
        ))
        prev_completed = await _is_room_completed(db, user_id, r)

    return PathDetail(
        id=str(path.id), slug=path.slug, title=path.title,
        description=path.description, icon=path.icon, rooms=rooms,
    )


@router.get("/rooms/{room_id}/lessons", response_model=list[LessonSummary])
async def list_room_lessons(room_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lesson).where(Lesson.room_id == room_id).order_by(Lesson.order_index)
    )
    lessons = result.scalars().all()

    lesson_ids = [l.id for l in lessons]
    completed_ids: set = set()
    if lesson_ids:
        result = await db.execute(
            select(UserLessonProgress.lesson_id)
            .where(UserLessonProgress.user_id == user_id)
            .where(UserLessonProgress.lesson_id.in_(lesson_ids))
        )
        completed_ids = {row[0] for row in result.all()}

    return [
        LessonSummary(
            id=str(l.id), title=l.title, order_index=l.order_index,
            completed=l.id in completed_ids,
        )
        for l in lessons
    ]


@router.get("/lessons/{lesson_id}", response_model=LessonDetail)
async def get_lesson_detail(lesson_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lesson).options(selectinload(Lesson.questions)).where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    q_ids = [q.id for q in lesson.questions]
    answered_ids: set = set()
    if q_ids:
        result = await db.execute(
            select(UserQuestionProgress.question_id)
            .where(UserQuestionProgress.user_id == user_id)
            .where(UserQuestionProgress.question_id.in_(q_ids))
        )
        answered_ids = {row[0] for row in result.all()}

    questions = [
        QuestionDetail(
            id=str(q.id), order_index=q.order_index,
            question_type=q.question_type.value,
            difficulty=q.difficulty.value,
            prompt=q.prompt,
            answered=q.id in answered_ids,
        )
        for q in lesson.questions
    ]

    result = await db.execute(
        select(UserLessonProgress)
        .where(UserLessonProgress.user_id == user_id)
        .where(UserLessonProgress.lesson_id == lesson.id)
    )
    completed = result.scalar_one_or_none() is not None

    result = await db.execute(
        select(Lesson.id, Lesson.order_index)
        .where(Lesson.room_id == lesson.room_id)
        .order_by(Lesson.order_index)
    )
    siblings = result.all()

    prev_id = None
    next_id = None
    for i, (sid, _ord) in enumerate(siblings):
        if str(sid) == str(lesson.id):
            if i > 0:
                prev_id = str(siblings[i - 1][0])
            if i < len(siblings) - 1:
                next_id = str(siblings[i + 1][0])
            break

    return LessonDetail(
        id=str(lesson.id), title=lesson.title,
        order_index=lesson.order_index, blocks=lesson.blocks,
        questions=questions, completed=completed,
        prev_lesson_id=prev_id, next_lesson_id=next_id,
    )


@router.post("/questions/{question_id}/start")
async def start_question(question_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LessonQuestion).where(LessonQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.question_type == QuestionType.text:
        return {"started": True, "type": "text"}

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    username = user.username if user else "player"

    session = await get_or_create_session(db, user_id)

    container = None
    for c in session.containers:
        if c.status == ContainerStatus.running:
            container = c
            break
    if container is None:
        container = await provision_container(db, session, username)

    setup_script = question.setup_script or ""
    setup_script = setup_script.replace("/home/player", f"/home/{username}").replace(
        "player:player", f"{username}:{username}"
    )

    if setup_script.strip():
        exec_id = _docker_client.api.exec_create(
            container.docker_container_id,
            ["/bin/bash", "-c", setup_script],
            user="root",
        )["Id"]
        output = _docker_client.api.exec_start(exec_id)
        inspect = _docker_client.api.exec_inspect(exec_id)
        print(f"QUESTION SETUP: q={question.id} container={container.docker_container_id[:12]} "
              f"exit_code={inspect.get('ExitCode')} output={output!r}")

    return {"started": True, "type": "terminal"}


@router.post("/questions/{question_id}/submit")
async def submit_answer(
    question_id: str,
    payload: AnswerSubmission,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LessonQuestion).where(LessonQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    expected_hash = question.answer_hash
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    username = user.username if user else None

    placeholders = {
        "{username}": username,
        "/home/{username}": f"/home/{username}" if username else None,
    }

    matched_placeholder = False
    for template, resolved in placeholders.items():
        if resolved is None:
            continue
        if _hash_answer(template) in (expected_hash.split("|") if expected_hash else []):
            matched_placeholder = True
            correct = _hash_answer(payload.answer) == _hash_answer(resolved)
            if correct:
                await _record_correct_answer(db, user_id, question.id)
                await _maybe_mark_lesson_complete(db, user_id, question.lesson_id)
                await check_auto_upgrade(db, user_id)
                return {"correct": True}
            else:
                await _record_wrong_first_attempt(db, user_id, question.id)
                return {"correct": False}

    if matched_placeholder:
        return {"correct": False}

    user_hash = _hash_answer(payload.answer)
    accepted = expected_hash.split("|") if expected_hash else []
    if user_hash not in accepted:
        await _record_wrong_first_attempt(db, user_id, question.id)
        return {"correct": False}

    result = await db.execute(
        select(UserQuestionProgress)
        .where(UserQuestionProgress.user_id == user_id)
        .where(UserQuestionProgress.question_id == question.id)
    )
    await _record_correct_answer(db, user_id, question.id)
    await _maybe_mark_lesson_complete(db, user_id, question.lesson_id)
    await check_auto_upgrade(db, user_id)
    return {"correct": True}


async def _record_correct_answer(db: AsyncSession, user_id, question_id):
    """
    Records that this question was answered correctly (progress row is the
    per-user, per-question existence marker). If a wrong attempt was recorded
    earlier, the first attempt wasn't correct: the flag is set accordingly and
    the tombstone row is consumed — the flag is the single source of truth.

    If the tombstone table is missing (deployed code ahead of migrations), we
    degrade gracefully: the answer still records, with an optimistic
    first_attempt_correct=True, instead of failing the submission.
    """
    result = await db.execute(
        select(UserQuestionProgress)
        .where(UserQuestionProgress.user_id == user_id)
        .where(UserQuestionProgress.question_id == question_id)
    )
    if result.scalar_one_or_none() is not None:
        return

    tombstone = None
    try:
        result = await db.execute(
            select(UserWrongAttempt)
            .where(UserWrongAttempt.user_id == user_id)
            .where(UserWrongAttempt.question_id == question_id)
        )
        tombstone = result.scalar_one_or_none()
    except ProgrammingError as e:
        await db.rollback()
        print(f"WARNING: user_wrong_attempts unavailable ({e.orig.__class__.__name__}); "
              f"recording answer with first_attempt_correct=True. Run: alembic upgrade head")
    if tombstone is not None:
        await db.delete(tombstone)

    db.add(UserQuestionProgress(
        user_id=user_id, question_id=question_id,
        first_attempt_correct=tombstone is None,
    ))
    await db.commit()


async def _record_wrong_first_attempt(db: AsyncSession, user_id, question_id):
    """
    A question is 'first-attempt correct' only if the very first submission
    for it was correct. A wrong submission for a question the user hasn't
    already answered correctly is recorded as a tombstone row in
    user_wrong_attempts, so it survives restarts and is visible to every
    worker process. The tombstone is consumed when the question is later
    answered correctly (see _record_correct_answer).
    """
    result = await db.execute(
        select(UserQuestionProgress)
        .where(UserQuestionProgress.user_id == user_id)
        .where(UserQuestionProgress.question_id == question_id)
    )
    if result.scalar_one_or_none() is not None:
        return  # already answered correctly previously; doesn't affect first-attempt status

    try:
        result = await db.execute(
            select(UserWrongAttempt)
            .where(UserWrongAttempt.user_id == user_id)
            .where(UserWrongAttempt.question_id == question_id)
        )
        if result.scalar_one_or_none() is None:
            db.add(UserWrongAttempt(user_id=user_id, question_id=question_id))
            await db.commit()
    except ProgrammingError as e:
        await db.rollback()
        print(f"WARNING: user_wrong_attempts unavailable ({e.orig.__class__.__name__}); "
              f"wrong attempt not recorded. Run: alembic upgrade head")


async def check_auto_upgrade(db: AsyncSession, user_id) -> None:
    """Algorithm 4 (spec 4.1): promote strict -> free after UPGRADE_WINDOW
    completed rooms if first-attempt accuracy across them is >= UPGRADE_THRESHOLD."""
    # Bail out early for free-mode/unknown users before doing any queries.
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or user.progression_mode != "strict":
        return

    result = await db.execute(
        select(UserLessonProgress, Lesson.room_id)
        .join(Lesson, Lesson.id == UserLessonProgress.lesson_id)
        .where(UserLessonProgress.user_id == user_id)
        .order_by(UserLessonProgress.completed_at.desc())
    )
    rows = result.all()

    seen_rooms = []
    for _progress, room_id in rows:
        if room_id not in seen_rooms:
            seen_rooms.append(room_id)

    # Most recently completed rooms (zero-question lessons count too — a
    # completed room with no questions still says something about accuracy).
    recent_room_ids = seen_rooms[:UPGRADE_WINDOW]
    if len(recent_room_ids) < UPGRADE_WINDOW:
        return

    result = await db.execute(
        select(Lesson.id).where(Lesson.room_id.in_(recent_room_ids))
    )
    lesson_ids = {row[0] for row in result.all()}
    if not lesson_ids:
        return

    result = await db.execute(
        select(LessonQuestion.id).where(LessonQuestion.lesson_id.in_(lesson_ids))
    )
    q_ids = {row[0] for row in result.all()}
    total_questions = len(q_ids)
    if total_questions == 0:
        return

    result = await db.execute(
        select(UserQuestionProgress)
        .where(UserQuestionProgress.user_id == user_id)
        .where(UserQuestionProgress.question_id.in_(q_ids))
    )
    progress_rows = result.scalars().all()

    first_attempt_correct_count = sum(
        1 for p in progress_rows if p.first_attempt_correct
    )

    accuracy = first_attempt_correct_count / total_questions
    if accuracy >= UPGRADE_THRESHOLD:
        user.progression_mode = "free"
        await db.commit()


async def _maybe_mark_lesson_complete(db: AsyncSession, user_id, lesson_id):
    """Mark lesson complete if all its questions are answered."""
    result = await db.execute(select(LessonQuestion.id).where(LessonQuestion.lesson_id == lesson_id))
    all_qids = {row[0] for row in result.all()}
    if not all_qids:
        result = await db.execute(
            select(UserLessonProgress)
            .where(UserLessonProgress.user_id == user_id)
            .where(UserLessonProgress.lesson_id == lesson_id)
        )
        if result.scalar_one_or_none() is None:
            db.add(UserLessonProgress(user_id=user_id, lesson_id=lesson_id))
            await db.commit()
        await check_auto_upgrade(db, user_id)
        return

    result = await db.execute(
        select(UserQuestionProgress.question_id)
        .where(UserQuestionProgress.user_id == user_id)
        .where(UserQuestionProgress.question_id.in_(all_qids))
    )
    answered = {row[0] for row in result.all()}

    if all_qids.issubset(answered):
        result = await db.execute(
            select(UserLessonProgress)
            .where(UserLessonProgress.user_id == user_id)
            .where(UserLessonProgress.lesson_id == lesson_id)
        )
        if result.scalar_one_or_none() is None:
            db.add(UserLessonProgress(user_id=user_id, lesson_id=lesson_id))
            await db.commit()
        await check_auto_upgrade(db, user_id)


class RecentActivityItem(BaseModel):
    type: str
    title: str
    completed_at: str


class DashboardStats(BaseModel):
    lessons_completed: int
    questions_answered: int
    total_score: int
    recent_activity: list[RecentActivityItem]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(func.count()).select_from(UserLessonProgress).where(UserLessonProgress.user_id == user_id)
    )
    lessons_completed = result.scalar_one()

    result = await db.execute(
        select(func.count()).select_from(UserQuestionProgress).where(UserQuestionProgress.user_id == user_id)
    )
    questions_answered = result.scalar_one()

    total_score = lessons_completed * 10 + questions_answered * 2

    result = await db.execute(
        select(UserLessonProgress.completed_at, Lesson.title)
        .join(Lesson, Lesson.id == UserLessonProgress.lesson_id)
        .where(UserLessonProgress.user_id == user_id)
        .order_by(UserLessonProgress.completed_at.desc())
        .limit(5)
    )
    recent = [
        RecentActivityItem(type="lesson", title=title, completed_at=completed_at.isoformat())
        for completed_at, title in result.all()
    ]

    return DashboardStats(
        lessons_completed=lessons_completed,
        questions_answered=questions_answered,
        total_score=total_score,
        recent_activity=recent,
    )
