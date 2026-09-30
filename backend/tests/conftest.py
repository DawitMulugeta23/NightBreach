import pytest_asyncio

from app.db.session import engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def database_engine_lifecycle():
    # Remove connections that may have been created before the test loop started.
    await engine.dispose()

    yield

    # Explicitly close all pooled connections before the pytest event loop closes.
    await engine.dispose()
