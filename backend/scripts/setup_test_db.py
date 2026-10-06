"""Create and migrate the isolated test database.  Run from backend/:
    python scripts/setup_test_db.py
The name is the development database name plus "_test" (override: TEST_DATABASE_URL).
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncpg
from sqlalchemy.engine import make_url

from app.config import Settings


def resolve_test_url():
    explicit = os.environ.get("TEST_DATABASE_URL")
    url = make_url(explicit) if explicit else make_url(Settings().database_url)
    if not explicit and not (url.database or "").endswith("_test"):
        url = url.set(database=f"{url.database}_test")
    if not (url.database or "").endswith("_test"):
        sys.exit(f"refusing: test database name must end in _test (got {url.database})")
    return url


def dsn(url, database=None):
    return url.set(drivername="postgresql", database=database or url.database).render_as_string(
        hide_password=False
    )


async def ensure_database(url) -> None:
    admin = await asyncpg.connect(dsn(url, "postgres"))
    try:
        exists = await admin.fetchval("select 1 from pg_database where datname = $1", url.database)
        if exists:
            print(f"database {url.database} already exists")
        else:
            await admin.execute(f'create database "{url.database}"')
            print(f"created database {url.database}")
    finally:
        await admin.close()


async def migrated_revision(url):
    conn = await asyncpg.connect(dsn(url))
    try:
        return await conn.fetchval("select version_num from alembic_version")
    except asyncpg.UndefinedTableError:
        return None
    finally:
        await conn.close()


def main() -> None:
    url = resolve_test_url()
    try:
        asyncio.run(ensure_database(url))
    except asyncpg.InsufficientPrivilegeError:
        sys.exit(
            f"role '{url.username}' cannot create databases. Run:\n"
            f"  sudo -u postgres psql -c 'ALTER ROLE \"{url.username}\" CREATEDB;'\n"
            "then re-run this script."
        )

    env = {**os.environ, "DATABASE_URL": url.render_as_string(hide_password=False)}
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], env=env, check=True)

    revision = asyncio.run(migrated_revision(url))
    if revision is None:
        sys.exit(
            "alembic did not migrate the test database; migrations/env.py probably ignores "
            "DATABASE_URL. Paste migrations/env.py and I will fix it."
        )
    print(f"{url.database} is at revision {revision}")


main()
