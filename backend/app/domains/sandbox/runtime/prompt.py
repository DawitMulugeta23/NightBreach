"""Learner-facing shell prompt identity for NightBreach practical environments.

The prompt format is fixed by the SRS (see Section 15.4):

    learner_username@DE=>M-[/]
    |_____$

The second line is a literal marker the learner sees before every command.
The first line shows the learner's username, the machine role indicator,
and the current working directory.
"""
from __future__ import annotations

import re

# Shell-safe characters we allow in the prompt. Usernames are validated at
# registration, but this is defence-in-depth against injection into the
# generated bashrc.
_SAFE_USERNAME = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")

# The literal marker shown on the second prompt line, then the command point.
_MARKER = "|_____$"

# Machine role to role tag. Attack Machine is "DE" (desktop environment).
_ROLE_TAG = "DE"


def build_prompt(username: str) -> str:
    """Return the two-line PS1 for the learner's interactive bash session."""
    if not _SAFE_USERNAME.match(username or ""):
        raise ValueError("Unsafe username for terminal prompt.")

    # Single-quote the whole PS1 so bash expands \\u, \\w itself.
    # bash substitutes \w -> current working directory, so the / in the
    # spec's "M-[/]" is the live CWD.
    line_one = (
        f"{username}@{_ROLE_TAG}=>M-[\\w]"
    )
    line_two = _MARKER

    return f"{line_one}\\n{line_two} "


def build_bashrc(username: str) -> str:
    """Return a bashrc fragment that installs the NightBreach prompt.

    Written to /tmp/nightbreach.bashrc inside the container and passed to
    bash via --rcfile so the container's own /etc/bash.bashrc is not
    modified.
    """
    ps1 = build_prompt(username)
    # Use single quotes around PS1 to avoid premature expansion.
    return (
        "# NightBreach learner prompt - injected by the runtime.\n"
        f"export PS1='{ps1}'\n"
        "# Keep history inside the container only.\n"
        "export HISTFILE=/tmp/.nb_history\n"
    )