"""Публикации: requires_auth; попытки прохождения: user_id

Revision ID: 0001_auth_passage
Revises:
Create Date: 2026-11-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_auth_passage"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    insp = sa.inspect(op.get_bind())
    return column in {c["name"] for c in insp.get_columns(table)}


def _has_index(table: str, index_name: str) -> bool:
    insp = sa.inspect(op.get_bind())
    return index_name in {ix["name"] for ix in insp.get_indexes(table)}


def _has_fk(table: str, fk_name: str) -> bool:
    insp = sa.inspect(op.get_bind())
    return fk_name in {fk["name"] for fk in insp.get_foreign_keys(table)}


def upgrade() -> None:
    # Идемпотентно: init_db (create_all) мог уже создать колонки.
    if not _has_column("training_publications", "requires_auth"):
        op.add_column(
            "training_publications",
            sa.Column(
                "requires_auth",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    if not _has_column("training_passage_attempts", "user_id"):
        op.add_column(
            "training_passage_attempts",
            sa.Column("user_id", sa.Integer(), nullable=True),
        )
    if not _has_fk("training_passage_attempts", "fk_passage_attempts_user"):
        op.create_foreign_key(
            "fk_passage_attempts_user",
            "training_passage_attempts",
            "users",
            ["user_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if not _has_index(
        "training_passage_attempts", "ix_training_passage_attempts_user_id"
    ):
        op.create_index(
            "ix_training_passage_attempts_user_id",
            "training_passage_attempts",
            ["user_id"],
        )


def downgrade() -> None:
    if _has_index(
        "training_passage_attempts", "ix_training_passage_attempts_user_id"
    ):
        op.drop_index(
            "ix_training_passage_attempts_user_id",
            table_name="training_passage_attempts",
        )
    if _has_fk("training_passage_attempts", "fk_passage_attempts_user"):
        op.drop_constraint(
            "fk_passage_attempts_user", "training_passage_attempts", type_="foreignkey"
        )
    if _has_column("training_passage_attempts", "user_id"):
        op.drop_column("training_passage_attempts", "user_id")
    if _has_column("training_publications", "requires_auth"):
        op.drop_column("training_publications", "requires_auth")
