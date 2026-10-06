#!/usr/bin/env python3
"""End-to-end check of the lab learning loop through the public API.
Needs a running backend and a TOKEN:   python scripts/e2e_lab_loop.py
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from uuid import uuid4

BASE = os.environ.get("BASE", "http://127.0.0.1:8000")
API = BASE + "/api/v1"
TOKEN = os.environ.get("TOKEN") or sys.exit("set TOKEN first")
ROOM_ID = "af73b7b5-e330-4a5d-9a78-b0cd262880c5"
LESSON_TITLE = "Linux File Permissions"
LAB_SLUG = "linux-file-permissions"
TARGET_PASSWORD = "Student#2024"
FLAG_RE = re.compile(r"NB\{[A-Za-z0-9_-]{8,64}\}")

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}".rstrip())
    if not ok:
        failures.append(label)


def call(method, path, body=None):
    request = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            raw, status = response.read(), response.status
    except urllib.error.HTTPError as error:
        raw, status = error.read(), error.code
    try:
        return status, (json.loads(raw) if raw else None)
    except ValueError:
        return status, raw.decode(errors="replace")


def request_field(openapi, path):
    schema = openapi["paths"][path]["post"]["requestBody"]["content"]["application/json"]["schema"]
    if "$ref" in schema:
        schema = openapi["components"]["schemas"][schema["$ref"].split("/")[-1]]
    properties = schema.get("properties", {})
    return (schema.get("required") or list(properties))[0]


def result_of(payload):
    if not isinstance(payload, dict):
        return None
    return payload.get("result") or (payload.get("attempt") or {}).get("result")


def lesson_status(lesson_id):
    status, payload = call("GET", f"/progress/lessons/{lesson_id}/completion-state")
    return payload.get("lesson_status") if isinstance(payload, dict) else f"HTTP {status}"


def attempt(activity_id, field, answer, environment_id=None):
    body = {"environment_id": environment_id} if environment_id else {}
    status, started = call("POST", f"/practice/activities/{activity_id}/attempts", body)
    if status not in (200, 201):
        return status, None
    status, submitted = call("POST", f"/practice/attempts/{started['id']}/submit", {field: answer})
    return status, submitted


def main():
    openapi = json.load(urllib.request.urlopen(BASE + "/openapi.json"))
    start_path = "/api/v1/practice/activities/{activity_id}/attempts"
    submit_path = "/api/v1/practice/attempts/{attempt_id}/submit"
    for needed in (start_path, submit_path, "/api/v1/progress/lessons/{lesson_id}/completion-state"):
        if needed not in openapi["paths"]:
            progress = [p for p in openapi["paths"] if "/practice/" in p or "/progress/" in p]
            sys.exit(f"missing path {needed}. Available:\n  " + "\n  ".join(progress))
    field = request_field(openapi, submit_path)

    # --- find the lesson and its two required activities -----------------
    _, room = call("GET", f"/rooms/{ROOM_ID}")
    lesson_ref = next(l for l in room["lessons"] if l.get("title") == LESSON_TITLE)
    _, lesson = call("GET", f"/lessons/{lesson_ref['id']}")
    lesson_id = lesson["id"]
    activities = [a for lp in lesson["lesson_practices"] for a in lp["practice"]["activities"]]
    quiz = next(a for a in activities if a["activity_type"] == "TEXT_QUESTION")
    lab_activity = next(a for a in activities if a["activity_type"] == "GUIDED_CTF")
    config = json.dumps(lab_activity.get("configuration", {}))
    check("lab activity shows lab_slug but no flag or secret",
          LAB_SLUG in config and "NB{" not in config and "secret" not in config.lower(), config)
    print(f"status before: {lesson_status(lesson_id)}")

    # --- quiz question ---------------------------------------------------
    _, quiz_result = attempt(quiz["id"], field, "Everyone on the system")
    check("quiz answered correctly", result_of(quiz_result) == "SUCCESS", str(result_of(quiz_result)))
    check("lesson is IN_PROGRESS after the quiz alone", lesson_status(lesson_id) == "IN_PROGRESS",
          lesson_status(lesson_id))

    # --- launch the lab ---------------------------------------------------
    status, lab = call("POST", f"/sandbox/labs/{LAB_SLUG}/launch")
    if status != 200:
        sys.exit(f"launch failed: {status} {lab}")
    environment_id = lab["environment_id"]
    print(f"environment: {environment_id}")

    try:
        check("lab is ready", lab["state"] == "ready", lab["state"])

        # --- the backend must refuse bad environments ---------------------
        status, _ = attempt(lab_activity["id"], field, "NB{perm_0000000000000000}", str(uuid4()))
        check("forged environment id is refused (404)", status == 404, f"HTTP {status}")
        status, _ = attempt(lab_activity["id"], field, "NB{perm_0000000000000000}")
        check("attempt without an environment is refused (409)", status == 409, f"HTTP {status}")

        # --- a wrong flag fails and does not complete the lesson ----------
        _, wrong = attempt(lab_activity["id"], field, "NB{perm_0000000000000000}", environment_id)
        check("wrong flag fails", result_of(wrong) == "FAILED", str(result_of(wrong)))
        check("lesson still IN_PROGRESS after a wrong flag", lesson_status(lesson_id) == "IN_PROGRESS",
              lesson_status(lesson_id))

        # --- the learner path, from inside the attack machine -------------
        target_ip = lab["network_subnet"].replace("0/24", "20")
        shell = (
            f"sshpass -p '{TARGET_PASSWORD}' ssh -o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 student@{target_ip} "
            "'cat /srv/backups/db-backup.sql' 2>&1"
        )
        found = subprocess.run(
            ["docker", "exec", f"nb-env-{environment_id}-machine-attacker", "sh", "-c", shell],
            capture_output=True, text=True, timeout=60,
        ).stdout
        match = FLAG_RE.search(found)
        check("flag recovered from the target through the attack machine", bool(match))

        # --- the real flag completes the practice and the lesson ----------
        if match:
            _, right = attempt(lab_activity["id"], field, match.group(0), environment_id)
            check("correct flag succeeds", result_of(right) == "SUCCESS", str(result_of(right)))
            check("lesson is COMPLETED", lesson_status(lesson_id) == "COMPLETED", lesson_status(lesson_id))
    finally:
        call("POST", f"/sandbox/environments/{environment_id}/terminate")

    print("\nALL CHECKS PASSED" if not failures else f"\n{len(failures)} CHECK(S) FAILED")
    sys.exit(1 if failures else 0)


main()
