"""Proves lab isolation and limits against the real Docker daemon.

Run from backend/:  PYTHONPATH=. python scripts/check_sandbox_isolation.py
Uses the local alpine image; creates and removes everything it makes.
"""
from __future__ import annotations

import sys
import uuid

from app.domains.sandbox.runtime.docker import DockerRuntimeProvider
from app.domains.sandbox.runtime.provider import RuntimeNetworkAttachment

IMAGE = "alpine:latest"
tag = uuid.uuid4().hex[:6]
runtime = DockerRuntimeProvider()
networks, machines, failures = [], [], []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")
    if not ok:
        failures.append(label)


def machine(name: str, net, address: str):
    created = runtime.create_machine(
        name=f"nbt-{tag}-{name}",
        image=IMAGE,
        command=["sleep", "300"],
        network_attachments=[
            RuntimeNetworkAttachment(network_id=net.id, ipv4_address=address)
        ],
    )
    machines.append(created)
    runtime.start_machine(machine_id=created.id)
    return created


def ping(source, address: str) -> bool:
    result = runtime.execute_command(
        machine_id=source.id,
        command=["ping", "-c", "1", "-W", "2", address],
    )
    return result.exit_code == 0


try:
    net_a = runtime.create_network(
        name=f"nbt-{tag}-a", subnet="10.77.1.0/24", gateway="10.77.1.1"
    )
    net_b = runtime.create_network(
        name=f"nbt-{tag}-b", subnet="10.77.2.0/24", gateway="10.77.2.1"
    )
    networks += [net_a, net_b]

    attacker_a = machine("attacker-a", net_a, "10.77.1.10")
    target_a = machine("target-a", net_a, "10.77.1.20")
    target_b = machine("target-b", net_b, "10.77.2.20")

    attrs = runtime.inspect_machine(machine_id=attacker_a.id)
    attached = set(attrs["NetworkSettings"]["Networks"])
    check("machine is on its lab network only", attached == {net_a.name}, str(attached))

    host = attrs["HostConfig"]
    check("not privileged", host["Privileged"] is False)
    check("memory limit 512m, swap disabled",
          host["Memory"] == 512 * 1024 * 1024 and host["MemorySwap"] == host["Memory"])
    check("cpu limit 1.0", host["NanoCpus"] == 1_000_000_000)
    check("pids limit 256", host["PidsLimit"] == 256)
    check("all capabilities dropped first", host["CapDrop"] == ["ALL"])
    check("no-new-privileges set", "no-new-privileges:true" in (host["SecurityOpt"] or []))
    check("no host bind mounts", not host.get("Binds"))

    check("attacker -> target (same lab) allowed", ping(attacker_a, "10.77.1.20"))
    check("attacker -> other lab blocked", not ping(attacker_a, "10.77.2.20"))
    check("attacker -> internet blocked", not ping(attacker_a, "1.1.1.1"))
finally:
    for item in machines:
        runtime.remove_machine(machine_id=item.id)
    for item in networks:
        runtime.remove_network(network_id=item.id)

print("\nRESULT:", "ALL CHECKS PASSED" if not failures else f"{len(failures)} FAILED")
sys.exit(1 if failures else 0)
