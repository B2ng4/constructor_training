"""training_hints_enabled

Revision ID: 8f4c2a1b9d11
Revises: f2a8c1d9e4b0
Create Date: 2026-03-27
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "8f4c2a1b9d11"
down_revision: Union[str, None] = "f2a8c1d9e4b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trainings",
        sa.Column(
            "hints_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("trainings", "hints_enabled")
