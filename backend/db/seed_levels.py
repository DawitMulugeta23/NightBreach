import asyncio
import hashlib
import re
from pathlib import Path

from sqlalchemy import select

from db.session import AsyncSessionLocal
from db.models import Level

LEVELS_ROOT = Path(__file__).resolve().parent.parent.parent / "levels"


def hash_flag(flag: str) -> str:
    return hashlib.sha256(flag.strip().encode()).hexdigest()


async def seed_levels():
    async with AsyncSessionLocal() as db:
        for tier_dir in sorted(LEVELS_ROOT.glob("tier-*")):
            tier_match = re.match(r"tier-(\d+)", tier_dir.name)
            if not tier_match:
                continue
            tier = int(tier_match.group(1))

            for level_dir in sorted(tier_dir.glob("level-*")):
                level_match = re.match(r"level-(\d+)", level_dir.name)
                if not level_match:
                    continue
                level_number = int(level_match.group(1))

                description_path = level_dir / "description.md"
                flag_path = level_dir / "flag.txt"
                setup_path = level_dir / "setup.sh"

                if not (description_path.exists() and flag_path.exists() and setup_path.exists()):
                    print(f"SKIPPING {level_dir} — missing required files")
                    continue

                description = description_path.read_text()
                flag = flag_path.read_text().strip()
                setup_script = setup_path.read_text()

                title_match = re.search(r"^#\s*(.+)$", description, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else level_dir.name

                result = await db.execute(
                    select(Level).where(Level.tier == tier, Level.level_number == level_number)
                )
                existing = result.scalar_one_or_none()

                if existing is not None:
                    existing.title = title
                    existing.description = description
                    existing.flag_hash = hash_flag(flag)
                    existing.setup_script = setup_script
                    print(f"Updated tier {tier} level {level_number}: {title}")
                else:
                    db.add(Level(
                        tier=tier,
                        level_number=level_number,
                        title=title,
                        description=description,
                        flag_hash=hash_flag(flag),
                        setup_script=setup_script,
                    ))
                    print(f"Added tier {tier} level {level_number}: {title}")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_levels())
