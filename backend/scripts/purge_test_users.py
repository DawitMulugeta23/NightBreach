"""Remove leftover automated-test accounts, and everything depending on them,
from the development database.

Dry run (default, rolls back):  python scripts/purge_test_users.py
Apply:                          python scripts/purge_test_users.py --apply
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncpg
from sqlalchemy.engine import make_url

from app.config import Settings

TEST_USER_WHERE = (
    "(username ~ '^(ctf_api|ctf_other|other|submit|history|reader|sandbox)_[0-9a-f]+$' "
    "OR username IN ('practice_api_user', 'learning_api_user'))"
)

FK_SQL = """
select c.conrelid::regclass::text  as child,
       a.attname                   as child_col,
       c.confrelid::regclass::text as parent,
       af.attname                  as parent_col
from pg_constraint c
join pg_attribute a  on a.attrelid  = c.conrelid  and a.attnum  = c.conkey[1]
join pg_attribute af on af.attrelid = c.confrelid and af.attnum = c.confkey[1]
where c.contype = 'f' and array_length(c.conkey, 1) = 1
"""


def quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


async def main(apply: bool) -> None:
    url = make_url(Settings().database_url).set(drivername="postgresql")
    conn = await asyncpg.connect(url.render_as_string(hide_password=False))

    by_parent: dict[str, list] = {}
    for row in await conn.fetch(FK_SQL):
        by_parent.setdefault(row["parent"], []).append(row)

    matched = await conn.fetchval(f"select count(*) from users where {TEST_USER_WHERE}")
    kept = [r[0] for r in await conn.fetch(
        f"select username from users where not {TEST_USER_WHERE} order by username")]
    print(f"database: {url.database}")
    print(f"test accounts matched: {matched}")
    print(f"accounts that will be kept ({len(kept)}): {kept[:40]}{' ...' if len(kept) > 40 else ''}")

    counts: dict[str, int] = {}

    async def purge(table: str, where: str, path: frozenset) -> None:
        for fk in by_parent.get(table, []):
            child = fk["child"]
            if child == table or child in path:
                continue
            sub = (
                f'{quote(fk["child_col"])} IN '
                f'(SELECT {quote(fk["parent_col"])} FROM {table} WHERE {where})'
            )
            await purge(child, sub, path | {table})
        status = await conn.execute(f"DELETE FROM {table} WHERE {where}")
        counts[table] = counts.get(table, 0) + int(status.split()[-1])

    transaction = conn.transaction()
    await transaction.start()
    try:
        await purge("users", TEST_USER_WHERE, frozenset())
    except Exception:
        await transaction.rollback()
        await conn.close()
        raise

    for table, n in sorted(counts.items(), key=lambda item: -item[1]):
        if n:
            print(f"  {n:6d}  {table}")

    if apply:
        await transaction.commit()
        print("APPLIED")
    else:
        await transaction.rollback()
        print("dry run: rolled back. Re-run with --apply to delete.")
    await conn.close()


asyncio.run(main("--apply" in sys.argv))
