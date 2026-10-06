"""Set a user's password.  Run from backend/:  python scripts/reset_password.py"""
import asyncio
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncpg
from sqlalchemy.engine import make_url

from app.config import Settings
from app.core.security import hash_password


async def main() -> None:
    username = input("username to reset: ").strip()
    password = getpass.getpass("new password: ")
    if getpass.getpass("repeat: ") != password or len(password) < 8:
        sys.exit("passwords differ or are shorter than 8 characters")

    url = make_url(Settings().database_url).set(drivername="postgresql")
    conn = await asyncpg.connect(url.render_as_string(hide_password=False))
    try:
        columns = [
            row["column_name"]
            for row in await conn.fetch(
                "select column_name from information_schema.columns "
                "where table_name = 'users' and column_name like '%password%'"
            )
        ]
        if len(columns) != 1:
            sys.exit(f"expected exactly one password column, found {columns}")
        print(await conn.execute(
            f'update users set "{columns[0]}" = $1 where username = $2',
            hash_password(password), username,
        ))
    finally:
        await conn.close()


asyncio.run(main())
