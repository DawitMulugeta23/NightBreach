"""Course content for the learning-path seeder.

Each module exposes its path dict; this package assembles them into the
SEED_DATA list consumed by db.seed_learning.
"""
from db.content.linux import PATH as LINUX_PATH
from db.content.networking import PATH as NETWORKING_PATH
from db.content.windows import PATH as WINDOWS_PATH
from db.content.cybersecurity_fundamentals import PATH as CYBERSEC_FUNDAMENTALS_PATH
from db.content.web_pentesting import PATH as WEB_PENTESTING_PATH
from db.content.network_pentesting import PATH as NETWORK_PENTESTING_PATH
from db.content.red_teaming import PATH as RED_TEAMING_PATH
from db.content.stubs import PATHS as STUB_PATHS

SEED_DATA = [
    LINUX_PATH,
    NETWORKING_PATH,
    WINDOWS_PATH,
    CYBERSEC_FUNDAMENTALS_PATH,
    WEB_PENTESTING_PATH,
    NETWORK_PENTESTING_PATH,
    RED_TEAMING_PATH,
    *STUB_PATHS,
]
