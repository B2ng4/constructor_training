"""Создание всех таблиц

Revision ID: f98f8f4532c1
Revises: 
Create Date: 2025-04-09 15:29:16.515451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f98f8f4532c1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('images',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('url', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('url')
    )
    op.create_table('typesactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('registration_at', sa.DateTime(), nullable=True),
    sa.Column('photo', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('trainings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('cover_image', sa.UUID(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['cover_image'], ['images.uuid'], ),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trainingsteps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('training_id', sa.Integer(), nullable=False),
    sa.Column('step_number', sa.Integer(), nullable=False),
    sa.Column('action_type_id', sa.Integer(), nullable=True),
    sa.Column('area', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('annotation', sa.Text(), nullable=True),
    sa.Column('image_uuid', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['action_type_id'], ['typesactions.id'], ),
    sa.ForeignKeyConstraint(['image_uuid'], ['images.uuid'], ),
    sa.ForeignKeyConstraint(['training_id'], ['trainings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trainingsteps')
    op.drop_table('trainings')
    op.drop_table('users')
    op.drop_table('typesactions')
    op.drop_table('images')
    # ### end Alembic commands ###
