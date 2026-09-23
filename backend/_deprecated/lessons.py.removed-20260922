from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.models import Lesson
from core.security import decode_access_token

router = APIRouter(prefix="/lessons", tags=["lessons"])


def _require_user(token: str) -> str:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return user_id


class LessonSummary(BaseModel):
    id: str
    order_index: int
    title: str


class LessonDetail(BaseModel):
    id: str
    order_index: int
    title: str
    blocks: list[dict]


@router.get("", response_model=list[LessonSummary])
async def list_lessons(token: str, db: AsyncSession = Depends(get_db)):
    _require_user(token)
    result = await db.execute(select(Lesson).order_by(Lesson.order_index))
    lessons = result.scalars().all()
    return [LessonSummary(id=str(l.id), order_index=l.order_index, title=l.title) for l in lessons]


@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson(lesson_id: str, token: str, db: AsyncSession = Depends(get_db)):
    _require_user(token)
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonDetail(id=str(lesson.id), order_index=lesson.order_index, title=lesson.title, blocks=lesson.blocks)
