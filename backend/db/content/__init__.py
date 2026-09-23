"""Course content for the learning-path seeder.

Each module exposes its path dict; this package assembles them into the
SEED_DATA list consumed by db.seed_learning.
"""
from db.content.linux import PATH as LINUX_PATH
from db.content.networking import PATH as NETWORKING_PATH
from db.content.windows import PATH as WINDOWS_PATH
from db.content.stubs import PATHS as STUB_PATHS

SEED_DATA = [LINUX_PATH, NETWORKING_PATH, WINDOWS_PATH, *STUB_PATHS]
