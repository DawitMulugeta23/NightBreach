from app.domains.sandbox.runtime.docker import DockerRuntimeProvider
from app.domains.sandbox.runtime.provider import RuntimeProvider


def get_runtime_provider() -> RuntimeProvider:
    return DockerRuntimeProvider()
