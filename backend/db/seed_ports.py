import asyncio

from sqlalchemy import text

from db.session import AsyncSessionLocal

PORT_RANGE_START = 20000
PORT_RANGE_END = 20100  # 100 ports for now; widen later as needed


async def seed_ports():
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("""
                INSERT INTO ports (port_number, is_claimed)
                SELECT generate_series(CAST(:start AS integer), CAST(:end AS integer)), false
                ON CONFLICT (port_number) DO NOTHING
            """),
            {"start": PORT_RANGE_START, "end": PORT_RANGE_END},
        )
        await session.commit()
        print(f"Seeded ports {PORT_RANGE_START}-{PORT_RANGE_END}")


if __name__ == "__main__":
    asyncio.run(seed_ports())
