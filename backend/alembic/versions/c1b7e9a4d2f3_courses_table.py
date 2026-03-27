"""courses_table

Revision ID: c1b7e9a4d2f3
Revises: 8f4c2a1b9d11
Create Date: 2026-03-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c1b7e9a4d2f3"
down_revision: Union[str, None] = "8f4c2a1b9d11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=True
        ),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_courses_creator_id"), "courses", ["creator_id"], unique=False
    )

    op.create_table(
        "course_trainings",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("training_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["training_uuid"], ["trainings.uuid"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("course_id", "training_uuid"),
    )


def downgrade() -> None:
    op.drop_table("course_trainings")
    op.drop_index(op.f("ix_courses_creator_id"), table_name="courses")
    op.drop_table("courses")
