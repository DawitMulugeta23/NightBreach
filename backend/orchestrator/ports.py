from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def claim_port(db: AsyncSession) -> int | None:
    """
    Atomically claims one free port from the pool.
    Uses SELECT ... FOR UPDATE SKIP LOCKED so concurrent async
    requests never claim the same port, and never block on each other.
    """
    result = await db.execute(
        text("""
            UPDATE ports
            SET is_claimed = true, claimed_at = now()
            WHERE port_number = (
                SELECT port_number FROM ports
                WHERE is_claimed = false
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING port_number
        """)
    )
    row = result.first()
    await db.commit()
    return row[0] if row else None


async def release_port(db: AsyncSession, port_number: int) -> None:
    await db.execute(
        text("UPDATE ports SET is_claimed = false, claimed_at = NULL WHERE port_number = :p"),
        {"p": port_number},
    )
    await db.commit()
