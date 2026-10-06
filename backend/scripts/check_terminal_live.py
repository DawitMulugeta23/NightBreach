"""Opens a real interactive shell on a real attacker container.

Run from backend/:  PYTHONPATH=. python scripts/check_terminal_live.py
Needs nightbreach/attacker:1.0. Cleans up everything it creates.
"""
from __future__ import annotations

import sys
import time
import uuid

from app.domains.sandbox.runtime.docker import DockerRuntimeProvider
from app.domains.sandbox.runtime.provider import RuntimeNetworkAttachment

tag = uuid.uuid4().hex[:6]
runtime = DockerRuntimeProvider()
machines, networks, failures = [], [], []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}".rstrip())
    if not ok:
        failures.append(label)


def read_until(shell, needle, seconds=8):
    seen, deadline = b"", time.monotonic() + seconds
    while time.monotonic() < deadline and needle not in seen:
        chunk = shell.read()
        if chunk is None:
            break
        seen += chunk
    return seen


shell = None
try:
    net = runtime.create_network(name=f"nbt-{tag}-term", subnet="10.77.9.0/24", gateway="10.77.9.1")
    networks.append(net)
    box = runtime.create_machine(
        name=f"nbt-{tag}-attacker",
        image="nightbreach/attacker:1.0",
        network_attachments=[RuntimeNetworkAttachment(network_id=net.id, ipv4_address="10.77.9.10")],
    )
    machines.append(box)
    runtime.start_machine(machine_id=box.id)

    shell = runtime.open_shell(machine_id=box.id)
    banner = read_until(shell, b"NIGHTBREACH")
    check("banner from the attack machine", b"NIGHTBREACH" in banner)

    shell.write(b"echo nb-$((6*7))-ok; id -un\n")
    out = read_until(shell, b"nb-42-ok")
    check("command output round-trips", b"nb-42-ok" in out, repr(out[-60:]))

    shell.resize(132, 43)
    shell.write(b"stty size\n")
    out = read_until(shell, b"43 132")
    check("terminal resize reaches the shell", b"43 132" in out, repr(out[-40:]))

    shell.write(b"exit\n")
    ended = False
    for _ in range(20):
        if shell.read() is None:
            ended = True
            break
    check("read() returns None after the shell exits", ended)
finally:
    if shell is not None:
        shell.close()
    for item in machines:
        runtime.remove_machine(machine_id=item.id)
    for item in networks:
        runtime.remove_network(network_id=item.id)

print("\nRESULT:", "ALL CHECKS PASSED" if not failures else f"{len(failures)} FAILED")
sys.exit(1 if failures else 0)
