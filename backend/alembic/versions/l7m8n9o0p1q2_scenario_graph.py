"""add persistent training scenario graph

Revision ID: l7m8n9o0p1q2
Revises: k6l7m8n9o0p1
Create Date: 2026-09-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "l7m8n9o0p1q2"
down_revision: Union[str, None] = "k6l7m8n9o0p1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trainings",
        sa.Column("scenario_start_step_id", sa.Integer(), nullable=True),
    )
    op.create_table(
        "training_transitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("training_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_step_id", sa.Integer(), nullable=False),
        sa.Column("target_step_id", sa.Integer(), nullable=True),
        sa.Column("trigger_type", sa.String(length=32), server_default="success", nullable=False),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("condition", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(["source_step_id"], ["training_steps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_step_id"], ["training_steps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["training_uuid"], ["trainings.uuid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_step_id",
            "target_step_id",
            "trigger_type",
            name="uq_training_transition_route",
        ),
    )
    op.create_index("ix_training_transitions_training_uuid", "training_transitions", ["training_uuid"])
    op.create_index("ix_training_transitions_source_step_id", "training_transitions", ["source_step_id"])
    op.create_index("ix_training_transitions_target_step_id", "training_transitions", ["target_step_id"])


def downgrade() -> None:
    op.drop_index("ix_training_transitions_target_step_id", table_name="training_transitions")
    op.drop_index("ix_training_transitions_source_step_id", table_name="training_transitions")
    op.drop_index("ix_training_transitions_training_uuid", table_name="training_transitions")
    op.drop_table("training_transitions")
    op.drop_column("trainings", "scenario_start_step_id")
