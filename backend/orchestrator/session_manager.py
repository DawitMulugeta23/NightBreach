from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Session, SessionStatus


async def get_or_create_session(db: AsyncSession, user_id: str) -> Session:
    """
    Returns the user's active session if one exists, otherwise creates one.
    Always re-fetches with selectinload(containers) so the returned object
    is safe to use in async contexts without triggering a lazy load.
    """
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.containers))
        .where(Session.user_id == user_id, Session.status == SessionStatus.active)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    session = Session(user_id=user_id, status=SessionStatus.active)
    db.add(session)
    await db.commit()

    result = await db.execute(
        select(Session)
        .options(selectinload(Session.containers))
        .where(Session.id == session.id)
    )
    return result.scalar_one()
