import asyncio
import re
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domains.sandbox.labs import flags
from app.domains.sandbox.labs.flags import (
    FLAG_SETTER,
    LabProvisioningError,
    check_flag,
    derive_flag,
    plant_lab_flags,
)
from app.domains.sandbox.labs.registry import (
    LABS,
    allocate_lab_subnet,
    get_lab,
)
from app.domains.sandbox.labs.service import build_lab_response
from app.domains.sandbox.runtime.provider import RuntimeCommandResult
from app.models.sandbox import EnvironmentState, MachineRole

SLUG = "linux-file-permissions"


def make_environment(secret="s3cret-value"):
    return SimpleNamespace(
        id=uuid4(),
        lab_slug=SLUG,
        lab_secret=secret,
        state=EnvironmentState.READY,
        expires_at=None,
        networks=[SimpleNamespace(subnet="10.200.1.0/24")],
        machines=[
            SimpleNamespace(name="attacker", runtime_machine_id="rt-attacker",
                            interfaces=[SimpleNamespace(address="10.200.1.10")]),
            SimpleNamespace(name="target", runtime_machine_id="rt-target",
                            interfaces=[SimpleNamespace(address="10.200.1.20")]),
        ],
    )


class FakeRuntime:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def execute_command(self, *, machine_id, command, timeout=None):
        self.calls.append((machine_id, list(command)))
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


OK = RuntimeCommandResult(exit_code=0, stdout="", stderr="")


# --- registry ---------------------------------------------------------------

@pytest.mark.parametrize("lab", list(LABS.values()))
def test_registry_labs_are_well_formed(lab):
    roles = {machine.role for machine in lab.machines}
    assert MachineRole.ATTACK in roles and MachineRole.TARGET in roles

    for machine in lab.machines:
        assert ":" in machine.image and not machine.image.endswith(":latest")
        assert 2 <= machine.host_octet <= 254

    octets = [machine.host_octet for machine in lab.machines]
    assert len(octets) == len(set(octets))

    names = {machine.name for machine in lab.machines}
    for objective in lab.objectives:
        assert objective.machine in names


def test_allocate_lab_subnet_skips_used_subnets():
    assert allocate_lab_subnet(set())[:2] == (1, "10.200.1.0/24")
    index, subnet, gateway = allocate_lab_subnet({"10.200.1.0/24", "10.200.2.0/24"})
    assert (index, subnet, gateway) == (3, "10.200.3.0/24", "10.200.3.1")


def test_allocate_lab_subnet_returns_none_when_exhausted():
    used = {f"10.200.{i}.0/24" for i in range(1, 251)}
    assert allocate_lab_subnet(used) is None


# --- flags ------------------------------------------------------------------

def test_flags_are_deterministic_and_scoped():
    objective = get_lab(SLUG).objectives[0]
    env_a, env_b = uuid4(), uuid4()

    first = derive_flag(secret="s", environment_id=env_a, objective=objective)
    assert first == derive_flag(secret="s", environment_id=env_a, objective=objective)
    assert first != derive_flag(secret="s", environment_id=env_b, objective=objective)
    assert first != derive_flag(secret="other", environment_id=env_a, objective=objective)
    assert re.fullmatch(r"NB\{perm_[0-9a-f]{16}\}", first)


def test_check_flag_is_exact_apart_from_surrounding_whitespace():
    assert check_flag(submission="  NB{perm_abc}\n", expected="NB{perm_abc}")
    assert not check_flag(submission="NB{perm_abd}", expected="NB{perm_abc}")
    assert not check_flag(submission="", expected="NB{perm_abc}")


def test_plant_runs_flag_setter_on_the_target_only(monkeypatch):
    monkeypatch.setattr(flags, "_RETRY_DELAY_SECONDS", 0)
    environment, runtime = make_environment(), FakeRuntime([OK])

    asyncio.run(plant_lab_flags(runtime, environment))

    expected = derive_flag(
        secret=environment.lab_secret,
        environment_id=environment.id,
        objective=get_lab(SLUG).objectives[0],
    )
    assert runtime.calls == [("rt-target", [FLAG_SETTER, expected])]


def test_plant_retries_until_the_machine_is_ready(monkeypatch):
    monkeypatch.setattr(flags, "_RETRY_DELAY_SECONDS", 0)
    runtime = FakeRuntime([
        RuntimeError("container not ready"),
        RuntimeCommandResult(exit_code=1, stdout="", stderr="busy"),
        OK,
    ])

    asyncio.run(plant_lab_flags(runtime, make_environment()))

    assert len(runtime.calls) == 3


def test_plant_failure_raises_without_leaking_the_flag(monkeypatch):
    monkeypatch.setattr(flags, "_RETRY_DELAY_SECONDS", 0)
    environment = make_environment()
    flag = derive_flag(
        secret=environment.lab_secret,
        environment_id=environment.id,
        objective=get_lab(SLUG).objectives[0],
    )
    failing = RuntimeCommandResult(exit_code=1, stdout="", stderr=f"bad flag {flag}")
    runtime = FakeRuntime([failing] * flags._PLANT_ATTEMPTS)

    with pytest.raises(LabProvisioningError) as caught:
        asyncio.run(plant_lab_flags(runtime, environment))

    assert flag not in str(caught.value)


def test_plant_rejects_environment_without_secret():
    with pytest.raises(LabProvisioningError):
        asyncio.run(plant_lab_flags(FakeRuntime([]), make_environment(secret=None)))


# --- response shape ---------------------------------------------------------

def test_lab_response_hides_target_address_and_secrets():
    environment = make_environment()
    dumped = build_lab_response(environment).model_dump_json()

    assert "10.200.1.10" in dumped          # attacker address is shown
    assert "10.200.1.20" not in dumped      # target must be discovered
    assert "10.200.1.0/24" in dumped        # lab subnet is shown
    assert environment.lab_secret not in dumped
    assert "NB{" not in dumped
