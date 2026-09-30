from unittest.mock import Mock

import pytest
from docker.errors import APIError, NotFound

from app.domains.sandbox.runtime.docker import (
    DockerRuntimeError,
    DockerRuntimeProvider,
)
from app.domains.sandbox.runtime.provider import RuntimeNetworkAttachment


def make_provider():
    client = Mock()
    provider = DockerRuntimeProvider(client=client)
    return provider, client


def test_create_machine_connects_requested_ipv4_address() -> None:
    provider, client = make_provider()

    container = Mock()
    container.id = "container-1"
    container.name = "nb-machine"

    network = Mock()
    network.id = "network-1"
    network.name = "lab-network"

    client.containers.create.return_value = container
    client.networks.get.return_value = network

    result = provider.create_machine(
        name="nb-machine",
        image="nightbreach/attack-machine:latest",
        network_attachments=(
            RuntimeNetworkAttachment(
                network_id="network-1",
                ipv4_address="10.10.0.10",
            ),
        ),
    )

    assert result.id == "container-1"
    assert result.name == "nb-machine"

    client.containers.create.assert_called_once_with(
        image="nightbreach/attack-machine:latest",
        name="nb-machine",
        detach=True,
    )

    client.networks.get.assert_called_once_with("network-1")

    network.connect.assert_called_once_with(
        container,
        ipv4_address="10.10.0.10",
    )


def test_create_machine_supports_attachment_without_ipv4() -> None:
    provider, client = make_provider()

    container = Mock()
    container.id = "container-1"
    container.name = "nb-machine"

    network = Mock()
    client.containers.create.return_value = container
    client.networks.get.return_value = network

    provider.create_machine(
        name="nb-machine",
        image="nightbreach/attack-machine:latest",
        network_attachments=(
            RuntimeNetworkAttachment(
                network_id="network-1",
            ),
        ),
    )

    network.connect.assert_called_once_with(container)


def test_create_machine_supports_multiple_network_attachments() -> None:
    provider, client = make_provider()

    container = Mock()
    container.id = "container-1"
    container.name = "nb-machine"

    network_one = Mock()
    network_two = Mock()

    client.containers.create.return_value = container
    client.networks.get.side_effect = [
        network_one,
        network_two,
    ]

    provider.create_machine(
        name="multi-homed",
        image="nightbreach/attack-machine:latest",
        network_attachments=(
            RuntimeNetworkAttachment(
                network_id="network-1",
                ipv4_address="10.10.0.10",
            ),
            RuntimeNetworkAttachment(
                network_id="network-2",
                ipv4_address="10.20.0.10",
            ),
        ),
    )

    assert client.networks.get.call_count == 2

    network_one.connect.assert_called_once_with(
        container,
        ipv4_address="10.10.0.10",
    )

    network_two.connect.assert_called_once_with(
        container,
        ipv4_address="10.20.0.10",
    )


def test_create_machine_wraps_docker_api_error() -> None:
    provider, client = make_provider()

    client.containers.create.side_effect = APIError(
        "container creation failed"
    )

    with pytest.raises(
        DockerRuntimeError,
        match="Failed to create Docker machine",
    ):
        provider.create_machine(
            name="broken-machine",
            image="nightbreach/attack-machine:latest",
            network_attachments=(),
        )


def test_create_machine_wraps_missing_network() -> None:
    provider, client = make_provider()

    container = Mock()
    container.id = "container-1"
    container.name = "broken-machine"

    client.containers.create.return_value = container
    client.networks.get.side_effect = NotFound(
        "network not found"
    )

    with pytest.raises(
        DockerRuntimeError,
        match="Failed to create Docker machine",
    ):
        provider.create_machine(
            name="broken-machine",
            image="nightbreach/attack-machine:latest",
            network_attachments=(
                RuntimeNetworkAttachment(
                    network_id="missing-network",
                    ipv4_address="10.10.0.10",
                ),
            ),
        )
