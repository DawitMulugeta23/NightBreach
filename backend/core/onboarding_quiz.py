"""
Onboarding quiz: a short, broad-coverage aptitude check used once at
registration to assign a user's initial progression_mode (Algorithm 1,
spec section 4.1). Correct answers live only here, server-side — never
sent to the client.
"""

FREE_MODE_THRESHOLD = 0.85

QUIZ_QUESTIONS = [
    {
        "id": "q1",
        "prompt": "What does the acronym 'IP' stand for in networking?",
        "options": [
            {"id": "a", "text": "Internet Protocol"},
            {"id": "b", "text": "Internal Path"},
            {"id": "c", "text": "Interface Port"},
            {"id": "d", "text": "Information Packet"},
        ],
        "correct_option_id": "a",
    },
    {
        "id": "q2",
        "prompt": "In Linux, which command lists the files in the current directory?",
        "options": [
            {"id": "a", "text": "cd"},
            {"id": "b", "text": "ls"},
            {"id": "c", "text": "pwd"},
            {"id": "d", "text": "mv"},
        ],
        "correct_option_id": "b",
    },
    {
        "id": "q3",
        "prompt": "What is the primary purpose of a firewall?",
        "options": [
            {"id": "a", "text": "Speed up internet connections"},
            {"id": "b", "text": "Store passwords securely"},
            {"id": "c", "text": "Control network traffic based on security rules"},
            {"id": "d", "text": "Compress files for storage"},
        ],
        "correct_option_id": "c",
    },
    {
        "id": "q4",
        "prompt": "You receive an email from your 'bank' asking you to click a link and enter your password to verify your account. What should you do?",
        "options": [
            {"id": "a", "text": "Click the link immediately to avoid losing account access"},
            {"id": "b", "text": "Reply with your password to confirm your identity"},
            {"id": "c", "text": "Go directly to the bank's known website instead of clicking the link"},
            {"id": "d", "text": "Forward it to friends to see if they got it too"},
        ],
        "correct_option_id": "c",
    },
    {
        "id": "q5",
        "prompt": "What does HTTPS provide that plain HTTP does not?",
        "options": [
            {"id": "a", "text": "Faster page loading"},
            {"id": "b", "text": "Encrypted communication between browser and server"},
            {"id": "c", "text": "Automatic virus scanning"},
            {"id": "d", "text": "Unlimited bandwidth"},
        ],
        "correct_option_id": "b",
    },
    {
        "id": "q6",
        "prompt": "What is a 'strong' password most likely to include?",
        "options": [
            {"id": "a", "text": "Your name and birth year"},
            {"id": "b", "text": "A short, common word like 'password123'"},
            {"id": "c", "text": "A long mix of unrelated words, numbers, and symbols"},
            {"id": "d", "text": "The same password you use everywhere, for consistency"},
        ],
        "correct_option_id": "c",
    },
]


def get_public_questions() -> list[dict]:
    """Questions and options only — no correct_option_id — safe to send to the client."""
    return [
        {"id": q["id"], "prompt": q["prompt"], "options": q["options"]}
        for q in QUIZ_QUESTIONS
    ]


def score_answers(answers: dict[str, str]) -> float:
    """
    answers: {question_id: chosen_option_id}
    Returns a score from 0.0 to 1.0. Unanswered or unknown question ids count as wrong.
    """
    correct = 0
    for q in QUIZ_QUESTIONS:
        if answers.get(q["id"]) == q["correct_option_id"]:
            correct += 1
    return correct / len(QUIZ_QUESTIONS)

UPGRADE_THRESHOLD = 0.90
UPGRADE_WINDOW = 2
