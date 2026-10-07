"""Temporary debug: run provision through the service layer with a traceback."""
import asyncio
import os
import sys
import traceback
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"))

os.environ.setdefault("DATABASE_URL", os.environ.get("DATABASE_URL", ""))
from app.config import get_settings  # noqa: E402

from app.db.session import AsyncSessionLocal  # noqa: E402
from app.domains.sandbox.services.environment_service import (  # noqa: E402
    EnvironmentService,
    InterfaceSpec,
    MachineSpec,
    NetworkSpec,
)
from app.domains.sandbox.runtime.provider import RuntimeProvider  # noqa: E402
from app.models.sandbox import Environment, EnvironmentState, MachineRole  # noqa: E402
from app.models.user import User  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sandbox_test_helpers import FakeRuntime  # noqa: E402


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.id).limit(1))
        learner_id = result.scalar_one_or_none()

        if learner_id is None:
            from datetime import datetime, timezone

            user = User(
                username=f"debug_{uuid4().hex[:8]}",
                email=f"debug_{uuid4().hex[:8]}@example.com",
                hashed_password="x",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            learner_id = user.id

        environment = Environment(
            learner_id=learner_id,
            activity_id="debug-provision",
            state=EnvironmentState.REQUESTED,
            state_version=1,
        )
        session.add(environment)
        await session.commit()
        await session.refresh(environment)

        runtime = FakeRuntime()
        service = EnvironmentService(session=session, runtime=runtime)

        try:
            env = await service.provision_environment(
                environment_id=environment.id,
                learner_id=learner_id,
                networks=(
                    NetworkSpec(
                        name="lab",
                        subnet="172.30.0.0/24",
                        gateway="172.30.0.1",
                    ),
                ),
                machines=(
                    MachineSpec(
                        name="attacker",
                        role=MachineRole.ATTACK,
                        image="ubuntu:24.04",
                        interfaces=(
                            InterfaceSpec(
                                name="eth0",
                                network_name="lab",
                                address="172.30.0.10",
                            ),
                        ),
                    ),
                    MachineSpec(
                        name="target",
                        role=MachineRole.TARGET,
                        image="ubuntu:24.04",
                        interfaces=(
                            InterfaceSpec(
                                name="eth0",
                                network_name="lab",
                                address="172.30.0.20",
                            ),
                        ),
                    ),
                ),
            )
            print("OK", env.state)
        except Exception:
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
