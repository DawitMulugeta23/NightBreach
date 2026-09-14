import asyncio

from db.session import AsyncSessionLocal
from orchestrator.session_manager import get_or_create_session
from orchestrator import provisioning

# Monkey-patch for this test only: use alpine with a long-running command
provisioning.BASE_IMAGE = "alpine"


async def main():
    async with AsyncSessionLocal() as db:
        session = await get_or_create_session(db, "test_provision_user")
        print(f"Session: {session.id}")

        container = await provisioning.provision_container(db, session)
        print(f"Container row: {container.id}")
        print(f"  docker_container_id: {container.docker_container_id}")
        print(f"  status: {container.status}")
        print(f"  port: {container.port_number}")


if __name__ == "__main__":
    asyncio.run(main())
