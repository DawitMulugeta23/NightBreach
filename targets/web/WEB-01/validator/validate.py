from __future__ import annotations

import sys
from urllib.error import URLError
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:8080"


def fetch(path: str) -> str:
    with urlopen(f"{BASE_URL}{path}", timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(
                f"{path} returned HTTP {response.status}"
            )
        return response.read().decode("utf-8")


def validate() -> None:
    root = fetch("/")
    robots = fetch("/robots.txt")
    internal = fetch("/internal/")

    if "NightBreach Web Server" not in root:
        raise RuntimeError("Root page marker not found.")

    if "/internal/" not in robots:
        raise RuntimeError("Expected /internal/ discovery entry not found.")

    if "WEB-01 discovery successful." not in internal:
        raise RuntimeError("Internal endpoint marker not found.")

    print("WEB-01 validation: PASS")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, URLError, RuntimeError) as exc:
        print(f"WEB-01 validation: FAIL - {exc}")
        sys.exit(1)
