from __future__ import annotations

from .questions import TREE, AnswerSet, TOOLS


LEVELS = ("NONE", "BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED")

# Which capability dimensions are foundational vs. supporting vs. specialization
# for each goal. Mirrors SRS 5.15.
_GAP_RULES = {
    "network_pentest": {
        "foundational": ("networking_knowledge", "linux_cli_knowledge"),
        "specialization": ("practical_security_experience",),
        "tool": ("nmap",),
    },
    "web_pentest": {
        "foundational": ("linux_cli_knowledge",),
        "specialization": ("web_security_knowledge",),
        "tool": ("burp",),
    },
    "red_team": {
        "foundational": ("networking_knowledge", "linux_cli_knowledge"),
        "specialization": ("practical_security_experience",),
        "tool": (),
    },
    "linux": {"foundational": ("linux_cli_knowledge",), "specialization": (), "tool": ()},
    "networking": {"foundational": ("networking_knowledge",), "specialization": (), "tool": ()},
    "defensive": {"foundational": ("networking_knowledge",), "specialization": (), "tool": ()},
    "fundamentals": {"foundational": ("computer_knowledge",), "specialization": (), "tool": ()},
    "ctf": {"foundational": ("linux_cli_knowledge",), "specialization": ("practical_security_experience",), "tool": ()},
    "general_skill": {"foundational": ("computer_knowledge",), "specialization": (), "tool": ()},
}


def _level_from_score(score: int) -> str:
    return LEVELS[max(0, min(4, score))]


def summarise(answers: AnswerSet) -> dict:
    """Compute capability levels, knowledge gaps, and recommended next steps.

    Returns the exact shape stored on LearnerProfile.
    """
    by_question = {q.id: q for q in TREE}

    # Resolve chosen option objects once.
    choices: dict[str, tuple[str, str, int]] = {}
    for question_id, option_id in answers.items():
        question = by_question.get(question_id)
        if question is None:
            continue
        for option in question.options:
            if option.id == option_id:
                choices[question_id] = (
                    question.dimension, option.label, option.score
                )
                break

    # Dimensions we score directly.
    dimensions: dict[str, int] = {}
    for question_id, (dimension, _label, score) in choices.items():
        # tool_experience uses a dict, handled separately below.
        if dimension == "tool_experience":
            continue
        if dimension == "goals":
            continue
        dimensions[dimension] = max(dimensions.get(dimension, 0), score)

    # Tool experience is multi-select.
    tools_used = {
        tool for tool in TOOLS if tool in (answers.get("tools") or "")
    }
    tool_scores = {tool: 2 for tool in tools_used}  # "Used with tutorials"-ish

    # Goal set.
    goals = [
        option.id for option in by_question["goals"].options
        if option.id in (answers.get("goals") or "")
    ] or ["fundamentals"]

    # Gap detection per goal.
    gaps: list[str] = []
    for goal in goals:
        rule = _GAP_RULES.get(goal, {})
        for dimension in rule.get("foundational", ()):
            if dimensions.get(dimension, 0) <= 1:
                gaps.append(f"{dimension}:foundational")
        for dimension in rule.get("specialization", ()):
            if dimensions.get(dimension, 0) <= 1:
                gaps.append(f"{dimension}:specialization")
        for tool in rule.get("tool", ()):
            if tool not in tools_used:
                gaps.append(f"tool:{tool}")

    # NightBreach is CLI-driven: no Linux/command-line experience is a
    # foundational gap whatever goal the learner picked.
    if dimensions.get("linux_cli_knowledge", 0) <= 1:
        gaps.append("linux_cli_knowledge:foundational")

    # Learning path recommendations (path slugs from the curriculum).
    recommended_paths: list[str] = []
    if dimensions.get("linux_cli_knowledge", 0) <= 1 or "linux" in gaps:
        recommended_paths.append("linux-fundamentals")
    if dimensions.get("networking_knowledge", 0) <= 2:
        recommended_paths.append("networking-fundamentals")
    if dimensions.get("computer_knowledge", 0) <= 1:
        recommended_paths.append("cybersecurity-fundamentals")
    if "web_pentest" in goals and dimensions.get("web_security_knowledge", 0) <= 2:
        recommended_paths.append("offensive-security")
    if not recommended_paths:
        recommended_paths.append("offensive-security")

    # Practice recommendation (SRS 6.12 / 6.13).
    recommended_practice: list[str] = []
    if dimensions.get("linux_cli_knowledge", 0) <= 2:
        recommended_practice.append("linux-cli-exercises")
    if "tool:nmap" in gaps:
        recommended_practice.append("guided-nmap-investigation")
    if not recommended_practice:
        recommended_practice.append("guided-network-investigation")

    # Challenge entry point (SRS 6.11).
    practical = dimensions.get("practical_security_experience", 0)
    if practical == 0:
        challenge = "HIGH_GUIDANCE"
    elif practical <= 2:
        challenge = "MODERATE_GUIDANCE"
    elif practical == 3:
        challenge = "LOW_GUIDANCE"
    else:
        challenge = "INDEPENDENT"

    # Personalized advice (SRS 6.15 / 6.16).
    advice_parts: list[str] = []
    if dimensions.get("linux_cli_knowledge", 0) <= 2:
        advice_parts.append(
            "Practice Linux and command-line fundamentals regularly. "
            "If you haven't dedicated time or a local machine yet, don't worry — "
            "practice here using the environment and questions provided by NightBreach."
        )
    if "tool:nmap" in gaps:
        advice_parts.append(
            "Nmap output interpretation is the next concrete skill: focus on "
            "identifying open ports and service versions from real scan output."
        )
    if not advice_parts:
        advice_parts.append(
            "You can go directly to Guided CTF Challenges. Revisit Learning when a "
            "challenge exposes a gap in your knowledge."
        )

    return {
        "technical_background": choices.get("background", (None, None, 0))[1],
        "computer_knowledge": _level_from_score(dimensions.get("computer_knowledge", 0)),
        "networking_knowledge": _level_from_score(dimensions.get("networking_knowledge", 0)),
        "linux_cli_knowledge": _level_from_score(dimensions.get("linux_cli_knowledge", 0)),
        "web_security_knowledge": _level_from_score(dimensions.get("web_security_knowledge", 0)),
        "practical_security_experience": _level_from_score(
            dimensions.get("practical_security_experience", 0)
        ),
        "tool_experience": tool_scores,
        "goals": goals,
        "knowledge_gaps": sorted(set(gaps)),
        "recommended_learning_paths": recommended_paths,
        "recommended_practice": recommended_practice,
        "challenge_recommendation": challenge,
        "personalized_advice": " ".join(advice_parts),
    }