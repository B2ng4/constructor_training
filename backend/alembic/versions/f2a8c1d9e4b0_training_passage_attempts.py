"""training_passage_attempts

Revision ID: f2a8c1d9e4b0
Revises: 7cf765b44913
Create Date: 2026-03-25

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "f2a8c1d9e4b0"
down_revision: Union[str, None] = "7cf765b44913"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "training_passage_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("publication_id", sa.Integer(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("wrong_attempts_total", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["publication_id"],
            ["training_publications.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_training_passage_attempts_pub_started",
        "training_passage_attempts",
        ["publication_id", "started_at"],
    )
    op.create_index(
        "ix_training_passage_attempts_pub_finished",
        "training_passage_attempts",
        ["publication_id", "finished_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_training_passage_attempts_pub_finished",
        table_name="training_passage_attempts",
    )
    op.drop_index(
        "ix_training_passage_attempts_pub_started",
        table_name="training_passage_attempts",
    )
    op.drop_table("training_passage_attempts")
