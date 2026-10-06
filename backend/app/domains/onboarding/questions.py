from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping

AnswerSet = Mapping[str, str]  # question_id -> option_id


@dataclass(frozen=True, slots=True)
class Option:
    id: str
    label: str
    score: int          # 0..4 -> NONE..ADVANCED
    capability: str     # dimension this option asserts


@dataclass(frozen=True, slots=True)
class Question:
    id: str
    dimension: str
    prompt: str
    options: tuple[Option, ...]
    next: Callable[[AnswerSet], str | None] = lambda _answers: None
    # `gate` is used for conditional follow-ups (SRS 5.8, 5.11).
    gate: Callable[[AnswerSet], bool] = lambda _answers: True


# --- Q1 Goals ---------------------------------------------------------------

GOALS = (
    "fundamentals", "linux", "networking",
    "web_pentest", "network_pentest", "red_team",
    "defensive", "ctf", "general_skill",
)

Q_GOALS = Question(
    id="goals",
    dimension="goals",
    prompt="What do you want to achieve on NightBreach?",
    options=tuple(
        Option(id=g, label=g.replace("_", " ").title(), score=0, capability="goals")
        for g in GOALS
    ),
)

# --- Q2 Technical background ------------------------------------------------

Q_BACKGROUND = Question(
    id="background",
    dimension="technical_background",
    prompt="What best describes your current technical background?",
    options=(
        Option("beginner", "Complete beginner", 0, "technical_background"),
        Option("student", "Student (IT/CS)", 1, "technical_background"),
        Option("it_support", "IT Support", 2, "technical_background"),
        Option("sysadmin", "Systems Administrator", 3, "technical_background"),
        Option("network_eng", "Network Engineer", 3, "technical_background"),
        Option("developer", "Software Developer", 3, "technical_background"),
        Option("devops", "DevOps / Cloud", 3, "technical_background"),
        Option("soc", "Security Analyst / SOC", 3, "technical_background"),
        Option("pentester", "Penetration Tester", 4, "technical_background"),
        Option("red", "Red Teamer", 4, "technical_background"),
        Option("other", "Other technical background", 2, "technical_background"),
    ),
)

# --- Q3 Computer experience -------------------------------------------------

Q_COMPUTER = Question(
    id="computer",
    dimension="computer_knowledge",
    prompt="How comfortable are you with computers and operating systems?",
    options=(
        Option("beginner", "Beginner", 1, "computer_knowledge"),
        Option("intermediate", "Intermediate", 2, "computer_knowledge"),
        Option("advanced", "Advanced", 4, "computer_knowledge"),
    ),
)

# --- Q4 Networking ----------------------------------------------------------

Q_NETWORKING = Question(
    id="networking",
    dimension="networking_knowledge",
    prompt="How comfortable are you with computer networking?",
    options=(
        Option("beginner", "Beginner", 1, "networking_knowledge"),
        Option("basic", "Basic", 2, "networking_knowledge"),
        Option("intermediate", "Intermediate", 3, "networking_knowledge"),
        Option("advanced", "Advanced", 4, "networking_knowledge"),
        Option("unsure", "Not sure", 0, "networking_knowledge"),
    ),
)

Q_NETWORKING_FOLLOWUP = Question(
    id="networking_followup",
    dimension="networking_knowledge",
    prompt="What is DNS primarily used for?",
    options=(
        Option("translate", "Translating domain names to IP addresses", 1, "networking_knowledge"),
        Option("dhcp", "Assigning dynamic IP addresses", 0, "networking_knowledge"),
        Option("encrypt", "Encrypting web traffic", 0, "networking_knowledge"),
        Option("unsure", "Not sure", 0, "networking_knowledge"),
    ),
    gate=lambda a: a.get("networking") in ("beginner", "unsure"),
)

# --- Q5 Linux / CLI ---------------------------------------------------------

Q_LINUX = Question(
    id="linux",
    dimension="linux_cli_knowledge",
    prompt="How much experience do you have with Linux or command-line environments?",
    options=(
        Option("none", "None", 0, "linux_cli_knowledge"),
        Option("basic", "Basic", 2, "linux_cli_knowledge"),
        Option("intermediate", "Intermediate", 3, "linux_cli_knowledge"),
        Option("proficient", "Proficient", 4, "linux_cli_knowledge"),
    ),
)

Q_LINUX_GREP = Question(
    id="linux_grep",
    dimension="linux_cli_knowledge",
    prompt="Which command would you use to search for a word inside a text file?",
    options=(
        Option("grep", "grep", 2, "linux_cli_knowledge"),
        Option("cat", "cat", 0, "linux_cli_knowledge"),
        Option("ls", "ls", 0, "linux_cli_knowledge"),
        Option("unsure", "Not sure", 0, "linux_cli_knowledge"),
    ),
    gate=lambda a: a.get("linux") in ("basic", "intermediate", "proficient"),
)

# --- Q6 Web security --------------------------------------------------------

Q_WEB = Question(
    id="web_security",
    dimension="web_security_knowledge",
    prompt="How familiar are you with web application security?",
    options=(
        Option("none", "None", 0, "web_security_knowledge"),
        Option("theory", "Theoretical knowledge", 1, "web_security_knowledge"),
        Option("beginner", "Beginner hands-on", 2, "web_security_knowledge"),
        Option("intermediate", "Intermediate hands-on", 3, "web_security_knowledge"),
        Option("advanced", "Advanced practical", 4, "web_security_knowledge"),
    ),
    gate=lambda a: any(
        g in (a.get("goals") or "")
        for g in ("web_pentest", "red_team")
    ),
)

Q_WEB_SQLI = Question(
    id="web_sqli",
    dimension="web_security_knowledge",
    prompt="What is SQL injection?",
    options=(
        Option("inject", "Injecting malicious input into SQL queries", 2, "web_security_knowledge"),
        Option("wireless", "Cracking a wireless network", 0, "web_security_knowledge"),
        Option("ddos", "Overloading a server with traffic", 0, "web_security_knowledge"),
        Option("unsure", "Not sure", 0, "web_security_knowledge"),
    ),
    gate=lambda a: a.get("web_security") in ("theory", "beginner", "intermediate", "advanced"),
)

# --- Q7 Practical security experience ---------------------------------------

Q_PRACTICAL = Question(
    id="practical",
    dimension="practical_security_experience",
    prompt="What practical cybersecurity experience do you currently have?",
    options=(
        Option("none", "None", 0, "practical_security_experience"),
        Option("guided", "Followed tutorials or guided exercises", 1, "practical_security_experience"),
        Option("beginner_ctf", "Completed beginner CTF rooms", 2, "practical_security_experience"),
        Option("regular_ctf", "Regularly solve CTF challenges", 3, "practical_security_experience"),
        Option("assessments", "Performed authorized security assessments", 4, "practical_security_experience"),
    ),
)

# --- Q8 Tool experience -----------------------------------------------------

TOOLS = ("nmap", "burp", "metasploit", "wireshark", "john", "hashcat")

Q_TOOLS = Question(
    id="tools",
    dimension="tool_experience",
    prompt="Which cybersecurity tools have you used? (select all that apply)",
    options=tuple(
        Option(id=t, label=t.title(), score=1, capability="tool_experience")
        for t in TOOLS
    ),
    gate=lambda a: (a.get("practical") or "none") != "none",
)

Q_NMAP = Question(
    id="nmap_version",
    dimension="tool_experience",
    prompt="Which command performs service/version detection against a target?",
    options=(
        Option("ping", "ping 192.168.1.1", 0, "tool_experience"),
        Option("nmap", "nmap -sV 192.168.1.1", 2, "tool_experience"),
        Option("netstat", "netstat", 0, "tool_experience"),
        Option("grep", "grep", 0, "tool_experience"),
    ),
    gate=lambda a: "nmap" in (a.get("tools") or ""),
)


TREE: tuple[Question, ...] = (
    Q_GOALS,
    Q_BACKGROUND,
    Q_COMPUTER,
    Q_NETWORKING,
    Q_NETWORKING_FOLLOWUP,
    Q_LINUX,
    Q_LINUX_GREP,
    Q_WEB,
    Q_WEB_SQLI,
    Q_PRACTICAL,
    Q_TOOLS,
    Q_NMAP,
)


def next_question(answers: AnswerSet) -> Question | None:
    """Return the first question whose id is unanswered and whose gate passes."""
    for question in TREE:
        if question.id in answers:
            continue
        if not question.gate(answers):
            continue
        return question
    return None