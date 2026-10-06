"""Prints an access token.  Usage: export TOKEN=$(python scripts/login.py)"""
import getpass
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000/api/v1"

sys.stderr.write("app username: ")
sys.stderr.flush()
username = sys.stdin.readline().strip()
password = getpass.getpass("password: ")

request = urllib.request.Request(
    f"{BASE}/auth/login",
    data=json.dumps({"username": username, "password": password}).encode(),
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(request) as response:
        body = json.load(response)
except urllib.error.HTTPError as error:
    sys.exit(f"login failed ({error.code}): {error.read().decode()[:200]}")

token = body.get("access_token")
if not token:
    sys.exit(f"unexpected response, keys: {list(body)}")
print(token)
