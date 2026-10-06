import os

import pytest
import pytest_asyncio
from sqlalchemy.engine import make_url

from app.config import Settings, get_settings


def _test_database_url() -> str:
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit

    url = make_url(Settings().database_url)
    if not (url.database or "").endswith("_test"):
        url = url.set(database=f"{url.database}_test")
    return url.render_as_string(hide_password=False)


# This must run before anything imports app.db.session, which builds the engine.
os.environ["DATABASE_URL"] = _test_database_url()
get_settings.cache_clear()

from app.db.session import engine  # noqa: E402

if not (engine.url.database or "").endswith("_test"):
    pytest.exit(
        "Refusing to run: tests must use a database whose name ends in '_test'.",
        returncode=2,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def database_engine_lifecycle():
    # Remove connections that may have been created before the test loop started.
    await engine.dispose()

    yield

    # Explicitly close all pooled connections before the pytest event loop closes.
    await engine.dispose()
