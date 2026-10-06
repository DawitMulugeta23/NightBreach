from unittest.mock import Mock

import pytest
from docker.errors import APIError, NotFound

from app.domains.sandbox.runtime.docker import (
    DockerRuntimeError,
    DockerRuntimeProvider,
)
from app.domains.sandbox.runtime.provider import (
    RuntimeMachineLimits,
    RuntimeNetworkAttachment,
)


def make_provider():
    client = Mock()
    provider = DockerRuntimeProvider(client=client)
    return provider, client


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


# ---------------------------------------------------------------------------
# Hardened create_machine / create_network
# ---------------------------------------------------------------------------


def configure_docker(client, networks):
    """networks: {network_id: network_name}. Returns (container, nets)."""
    nets = {}

    for network_id, network_name in networks.items():
        net = Mock()
        net.id = network_id
        net.name = network_name
        nets[network_id] = net

    client.networks.get.side_effect = lambda network_id: nets[network_id]
    client.api.create_container.return_value = {"Id": "container-1"}

    container = Mock()
    container.id = "container-1"
    container.name = "nb-machine"
    client.containers.get.return_value = container

    return container, nets


def create_single_network_machine(provider, **kwargs):
    return provider.create_machine(
        name="nb-machine",
        image="nightbreach/attacker:1.0",
        network_attachments=(
            RuntimeNetworkAttachment(
                network_id="network-1",
                ipv4_address="10.10.0.10",
            ),
        ),
        **kwargs,
    )


def test_create_machine_is_created_on_lab_network_only() -> None:
    provider, client = make_provider()
    container, nets = configure_docker(client, {"network-1": "lab-network"})

    result = create_single_network_machine(provider)

    assert result.id == "container-1"
    assert result.name == "nb-machine"

    host_kwargs = client.api.create_host_config.call_args.kwargs
    assert host_kwargs["network_mode"] == "lab-network"

    client.api.create_endpoint_config.assert_called_once_with(
        ipv4_address="10.10.0.10",
    )

    create_kwargs = client.api.create_container.call_args.kwargs
    assert create_kwargs["image"] == "nightbreach/attacker:1.0"
    assert create_kwargs["name"] == "nb-machine"

    # Joining the lab network at creation means the container never touches
    # the default bridge, and no second connect() call is needed.
    nets["network-1"].connect.assert_not_called()


def test_create_machine_applies_restrictive_defaults() -> None:
    provider, client = make_provider()
    configure_docker(client, {"network-1": "lab-network"})

    create_single_network_machine(provider)

    host_kwargs = client.api.create_host_config.call_args.kwargs

    assert host_kwargs["privileged"] is False
    assert host_kwargs["cap_drop"] == ["ALL"]
    assert "ALL" not in host_kwargs["cap_add"]
    assert "SYS_ADMIN" not in host_kwargs["cap_add"]
    assert "NET_ADMIN" not in host_kwargs["cap_add"]
    assert host_kwargs["security_opt"] == ["no-new-privileges:true"]
    assert host_kwargs["mem_limit"] == "512m"
    assert host_kwargs["memswap_limit"] == "512m"
    assert host_kwargs["nano_cpus"] == 1_000_000_000
    assert host_kwargs["pids_limit"] == 256
    assert host_kwargs["ipc_mode"] == "private"
    assert "binds" not in host_kwargs
    assert "volumes" not in host_kwargs


def test_create_machine_applies_custom_limits() -> None:
    provider, client = make_provider()
    configure_docker(client, {"network-1": "lab-network"})

    create_single_network_machine(
        provider,
        limits=RuntimeMachineLimits(
            memory="256m",
            cpus=0.5,
            pids=64,
            capabilities=("SETUID", "SETGID"),
            read_only_rootfs=True,
            user="learner",
        ),
    )

    host_kwargs = client.api.create_host_config.call_args.kwargs
    assert host_kwargs["mem_limit"] == "256m"
    assert host_kwargs["nano_cpus"] == 500_000_000
    assert host_kwargs["pids_limit"] == 64
    assert host_kwargs["cap_add"] == ["SETUID", "SETGID"]
    assert host_kwargs["read_only"] is True
    assert host_kwargs["tmpfs"]

    create_kwargs = client.api.create_container.call_args.kwargs
    assert create_kwargs["user"] == "learner"


def test_create_machine_can_disable_no_new_privileges_for_suid_targets() -> None:
    provider, client = make_provider()
    configure_docker(client, {"network-1": "lab-network"})

    create_single_network_machine(
        provider,
        limits=RuntimeMachineLimits(no_new_privileges=False),
    )

    host_kwargs = client.api.create_host_config.call_args.kwargs
    assert host_kwargs["security_opt"] == []
    assert host_kwargs["privileged"] is False
    assert host_kwargs["cap_drop"] == ["ALL"]


def test_create_machine_supports_attachment_without_ipv4() -> None:
    provider, client = make_provider()
    configure_docker(client, {"network-1": "lab-network"})

    provider.create_machine(
        name="nb-machine",
        image="nightbreach/attacker:1.0",
        network_attachments=(
            RuntimeNetworkAttachment(network_id="network-1"),
        ),
    )

    client.api.create_endpoint_config.assert_called_once_with(
        ipv4_address=None,
    )


def test_create_machine_connects_additional_networks() -> None:
    provider, client = make_provider()
    container, nets = configure_docker(
        client,
        {"network-1": "net-one", "network-2": "net-two"},
    )

    provider.create_machine(
        name="nb-machine",
        image="nightbreach/attacker:1.0",
        network_attachments=(
            RuntimeNetworkAttachment(
                network_id="network-1", ipv4_address="10.10.0.10"
            ),
            RuntimeNetworkAttachment(
                network_id="network-2", ipv4_address="10.20.0.10"
            ),
        ),
    )

    host_kwargs = client.api.create_host_config.call_args.kwargs
    assert host_kwargs["network_mode"] == "net-one"

    nets["network-1"].connect.assert_not_called()
    nets["network-2"].connect.assert_called_once_with(
        container,
        ipv4_address="10.20.0.10",
    )


def test_create_machine_requires_a_network_attachment() -> None:
    provider, client = make_provider()

    with pytest.raises(
        DockerRuntimeError,
        match="requires at least one network attachment",
    ):
        provider.create_machine(
            name="nb-machine",
            image="nightbreach/attacker:1.0",
            network_attachments=(),
        )

    client.api.create_container.assert_not_called()


def test_create_machine_wraps_docker_api_error() -> None:
    provider, client = make_provider()
    configure_docker(client, {"network-1": "lab-network"})

    client.api.create_container.side_effect = APIError(
        "container creation failed"
    )

    with pytest.raises(
        DockerRuntimeError,
        match="Failed to create Docker machine",
    ):
        create_single_network_machine(provider)


def test_create_machine_removes_container_if_extra_network_connect_fails() -> None:
    provider, client = make_provider()
    container, nets = configure_docker(
        client,
        {"network-1": "net-one", "network-2": "net-two"},
    )
    nets["network-2"].connect.side_effect = APIError("connect failed")

    with pytest.raises(
        DockerRuntimeError,
        match="Failed to create Docker machine",
    ):
        provider.create_machine(
            name="nb-machine",
            image="nightbreach/attacker:1.0",
            network_attachments=(
                RuntimeNetworkAttachment(network_id="network-1"),
                RuntimeNetworkAttachment(network_id="network-2"),
            ),
        )

    container.remove.assert_called_once_with(force=True)


def test_create_network_is_internal_by_default() -> None:
    provider, client = make_provider()
    client.networks.create.return_value = Mock(id="network-1", name="lab")

    provider.create_network(
        name="lab",
        subnet="10.10.0.0/24",
        gateway="10.10.0.1",
    )

    kwargs = client.networks.create.call_args.kwargs
    assert kwargs["internal"] is True
    assert kwargs["driver"] == "bridge"
    assert kwargs["labels"] == {"nightbreach.managed": "true"}


def test_create_network_can_be_made_external_explicitly() -> None:
    provider, client = make_provider()
    client.networks.create.return_value = Mock(id="network-1", name="lab")

    provider.create_network(name="lab", internal=False)

    assert client.networks.create.call_args.kwargs["internal"] is False
