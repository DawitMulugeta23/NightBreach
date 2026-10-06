"""End-to-end check of the attacker + linux-permissions target images.

Run from backend/:  PYTHONPATH=. python scripts/check_lab_images.py
Needs the images from lab-images/build.sh. Cleans up everything it creates.
"""
from __future__ import annotations

import sys
import uuid

from app.domains.sandbox.runtime.docker import DockerRuntimeProvider
from app.domains.sandbox.runtime.provider import (
    DEFAULT_CAPABILITIES,
    RuntimeMachineLimits,
    RuntimeNetworkAttachment,
)

ATTACKER_IMAGE = "nightbreach/attacker:1.0"
TARGET_IMAGE = "nightbreach/linux-permissions-target:1.0"
SUBNET, GATEWAY = "10.77.3.0/24", "10.77.3.1"
ATTACKER_IP, TARGET_IP = "10.77.3.10", "10.77.3.20"
TEST_FLAG = "NB{test_flag_for_image_check}"
PASSWORD = "Student#2024"

tag = uuid.uuid4().hex[:6]
runtime = DockerRuntimeProvider()
networks, machines, failures = [], [], []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}".rstrip())
    if not ok:
        failures.append(label)


def run(machine, shell_command: str):
    return runtime.execute_command(
        machine_id=machine.id, command=["sh", "-c", shell_command]
    )


def ssh(machine, remote_command: str):
    return run(
        machine,
        f"sshpass -p '{PASSWORD}' ssh -o StrictHostKeyChecking=no "
        f"-o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 "
        f"student@{TARGET_IP} \"{remote_command}\" 2>&1",
    )


def make(name, image, ip, net, limits=None):
    created = runtime.create_machine(
        name=f"nbt-{tag}-{name}",
        image=image,
        limits=limits,
        network_attachments=[
            RuntimeNetworkAttachment(network_id=net.id, ipv4_address=ip)
        ],
    )
    machines.append(created)
    runtime.start_machine(machine_id=created.id)
    return created


try:
    net = runtime.create_network(name=f"nbt-{tag}-lab", subnet=SUBNET, gateway=GATEWAY)
    networks.append(net)

    attacker = make("attacker", ATTACKER_IMAGE, ATTACKER_IP, net)
    target_limits = RuntimeMachineLimits(
        memory="256m",
        pids=128,
        capabilities=DEFAULT_CAPABILITIES + ("SYS_CHROOT",),
    )
    target = make("target", TARGET_IMAGE, TARGET_IP, net, target_limits)

    import time
    time.sleep(3)  # let sshd come up

    # --- plant a per-lab flag the way the backend will ---
    planted = run(target, f"/usr/local/sbin/nb-set-flag '{TEST_FLAG}'")
    check("backend can plant flag as root", planted.exit_code == 0, planted.stdout.strip())

    # --- attacker machine ---
    check("attacker runs as non-root learner", run(attacker, "id -un").stdout.strip() == "learner")
    check("attacker has no sudo", run(attacker, "command -v sudo").exit_code != 0)
    for tool in ("nmap", "nc", "ssh", "sshpass", "curl", "ping"):
        check(f"attacker has {tool}", run(attacker, f"command -v {tool}").exit_code == 0)

    # --- network ---
    check("attacker -> target ping", run(attacker, f"ping -c 1 -W 2 {TARGET_IP}").exit_code == 0)
    scan = run(attacker, f"nmap -Pn -sT -p 22 {TARGET_IP}")
    check("nmap finds target ssh (22/tcp open)", "22/tcp open" in scan.stdout, scan.stdout.splitlines()[-3] if scan.stdout else "")
    check("attacker -> internet blocked", run(attacker, "ping -c 1 -W 2 1.1.1.1").exit_code != 0)

    # --- the intended learner path ---
    login = ssh(attacker, "id -un")
    check("student can ssh from attacker", login.stdout.strip().endswith("student"), login.stdout.strip()[-60:])
    listing = ssh(attacker, "ls -l /srv/backups")
    check("ls -l shows db-backup.sql world-readable", "-rw-r--r--" in listing.stdout and "db-backup.sql" in listing.stdout)
    check("ls -l shows payroll.csv protected", "-rw-r-----" in listing.stdout and "payroll.csv" in listing.stdout)
    leak = ssh(attacker, "cat /srv/backups/db-backup.sql")
    check("misconfiguration leaks the flag", TEST_FLAG in leak.stdout)
    denied = ssh(attacker, "cat /srv/backups/payroll.csv")
    check("payroll.csv correctly denied", "Permission denied" in denied.stdout)
    check("student cannot read /etc/shadow", "Permission denied" in ssh(attacker, "cat /etc/shadow").stdout)
    check("student cannot run nb-set-flag", "Permission denied" in ssh(attacker, "/usr/local/sbin/nb-set-flag NB{abcdefgh}").stdout)

    # --- container boundary ---
    host = runtime.inspect_machine(machine_id=target.id)["HostConfig"]
    check("target not privileged", host["Privileged"] is False)
    check("target drops ALL then re-adds", host["CapDrop"] == ["ALL"])
    check("target has no host mounts", not host.get("Binds"))
    check("target memory limit 256m", host["Memory"] == 256 * 1024 * 1024)

    # --- reset restores the vulnerable starting state ---
    run(target, "chmod 0600 /srv/backups/db-backup.sql")
    runtime.remove_machine(machine_id=target.id)
    machines.remove(target)
    target = make("target2", TARGET_IMAGE, TARGET_IP, net, target_limits)
    time.sleep(3)
    mode = run(target, "stat -c %a /srv/backups/db-backup.sql").stdout.strip()
    check("recreated target is back to 644 (reset works)", mode == "644", mode)
finally:
    for item in machines:
        runtime.remove_machine(machine_id=item.id)
    for item in networks:
        runtime.remove_network(network_id=item.id)

print("\nRESULT:", "ALL CHECKS PASSED" if not failures else f"{len(failures)} FAILED")
sys.exit(1 if failures else 0)
