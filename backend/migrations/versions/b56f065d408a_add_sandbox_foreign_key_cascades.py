"""add sandbox foreign key cascades

Revision ID: b56f065d408a
Revises: 49a274e32ca3
Create Date: 2026-09-29 01:26:21.396246

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b56f065d408a"
down_revision: Union[str, Sequence[str], None] = "49a274e32ca3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add database-level cascade behavior to Sandbox foreign keys."""

    op.drop_constraint(
        "sandbox_environment_machines_environment_id_fkey",
        "sandbox_environment_machines",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_environment_machines_environment_id_fkey",
        "sandbox_environment_machines",
        "sandbox_environments",
        ["environment_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "sandbox_environment_networks_environment_id_fkey",
        "sandbox_environment_networks",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_environment_networks_environment_id_fkey",
        "sandbox_environment_networks",
        "sandbox_environments",
        ["environment_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "sandbox_machine_interfaces_machine_id_fkey",
        "sandbox_machine_interfaces",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_machine_interfaces_machine_id_fkey",
        "sandbox_machine_interfaces",
        "sandbox_environment_machines",
        ["machine_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "sandbox_machine_interfaces_network_id_fkey",
        "sandbox_machine_interfaces",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_machine_interfaces_network_id_fkey",
        "sandbox_machine_interfaces",
        "sandbox_environment_networks",
        ["network_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Remove database-level cascade behavior from Sandbox foreign keys."""

    op.drop_constraint(
        "sandbox_machine_interfaces_network_id_fkey",
        "sandbox_machine_interfaces",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_machine_interfaces_network_id_fkey",
        "sandbox_machine_interfaces",
        "sandbox_environment_networks",
        ["network_id"],
        ["id"],
    )

    op.drop_constraint(
        "sandbox_machine_interfaces_machine_id_fkey",
        "sandbox_machine_interfaces",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_machine_interfaces_machine_id_fkey",
        "sandbox_machine_interfaces",
        "sandbox_environment_machines",
        ["machine_id"],
        ["id"],
    )

    op.drop_constraint(
        "sandbox_environment_networks_environment_id_fkey",
        "sandbox_environment_networks",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_environment_networks_environment_id_fkey",
        "sandbox_environment_networks",
        "sandbox_environments",
        ["environment_id"],
        ["id"],
    )

    op.drop_constraint(
        "sandbox_environment_machines_environment_id_fkey",
        "sandbox_environment_machines",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "sandbox_environment_machines_environment_id_fkey",
        "sandbox_environment_machines",
        "sandbox_environments",
        ["environment_id"],
        ["id"],
    )
