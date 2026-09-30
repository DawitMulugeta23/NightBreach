from uuid import uuid4

import pytest

from app.db.session import AsyncSessionLocal
from app.domains.sandbox.repositories.environment_repository import (
    EnvironmentRepository,
)
from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentNetwork,
    EnvironmentState,
    MachineInterface,
    MachineRole,
)
from app.models.user import User


@pytest.mark.asyncio
async def test_environment_repository_persists_environment_graph() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            learner = User(
                username=f"sandbox_{uuid4().hex[:10]}",
                email=f"{uuid4().hex[:12]}@example.test",
                hashed_password="test-hash",
            )
            session.add(learner)
            await session.flush()

            repository = EnvironmentRepository(session)

            environment = Environment(
                learner_id=learner.id,
                activity_id="WEB-01",
                state=EnvironmentState.REQUESTED,
                state_version=1,
            )

            created = await repository.create(environment)

            assert created.id == environment.id
            assert created.learner_id == learner.id
            assert created.activity_id == "WEB-01"
            assert created.state == EnvironmentState.REQUESTED
            assert created.state_version == 1

            network = await repository.add_network(
                EnvironmentNetwork(
                    environment_id=environment.id,
                    name="lab-network",
                    subnet="10.10.0.0/24",
                    gateway="10.10.0.1",
                )
            )

            machine = await repository.add_machine(
                EnvironmentMachine(
                    environment_id=environment.id,
                    name="attack-machine",
                    role=MachineRole.ATTACK,
                    image="nightbreach/attack-machine:latest",
                )
            )

            interface = await repository.add_interface(
                MachineInterface(
                    machine_id=machine.id,
                    network_id=network.id,
                    name="eth0",
                    address="10.10.0.10",
                )
            )

            retrieved = await repository.get_by_id(environment.id)

            assert retrieved is not None
            assert retrieved.id == environment.id
            assert retrieved.learner_id == learner.id
            assert retrieved.activity_id == "WEB-01"

            retrieved_for_learner = await repository.get_for_learner(
                environment_id=environment.id,
                learner_id=learner.id,
            )

            assert retrieved_for_learner is not None
            assert retrieved_for_learner.id == environment.id
            assert retrieved_for_learner.state == EnvironmentState.REQUESTED

            assert len(retrieved_for_learner.networks) == 1
            assert retrieved_for_learner.networks[0].name == "lab-network"
            assert retrieved_for_learner.networks[0].subnet == "10.10.0.0/24"
            assert retrieved_for_learner.networks[0].gateway == "10.10.0.1"

            assert len(retrieved_for_learner.machines) == 1
            retrieved_machine = retrieved_for_learner.machines[0]
            assert retrieved_machine.name == "attack-machine"
            assert retrieved_machine.role == MachineRole.ATTACK
            assert retrieved_machine.image == "nightbreach/attack-machine:latest"

            assert len(retrieved_machine.interfaces) == 1
            retrieved_interface = retrieved_machine.interfaces[0]
            assert retrieved_interface.name == "eth0"
            assert retrieved_interface.address == "10.10.0.10"
            assert retrieved_interface.network_id == network.id

            wrong_learner = await repository.get_for_learner(
                environment_id=environment.id,
                learner_id=uuid4(),
            )

            assert wrong_learner is None

            assert network.environment_id == environment.id
            assert machine.environment_id == environment.id
            assert machine.role == MachineRole.ATTACK
            assert interface.machine_id == machine.id
            assert interface.network_id == network.id
