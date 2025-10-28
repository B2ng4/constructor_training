# models/trainings.py

import uuid
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import UUID4
from sqlalchemy import ForeignKey, JSON, Enum, text, func, Table, Column, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.core.database import Base
import sqlalchemy as sa

# ==========================================================================
# Таблица тегов многие-ко-многим
# ==========================================================================
training_tags = Table(
    "training_tags",
    Base.metadata,
    Column("training_uuid", UUID(as_uuid=True), ForeignKey("trainings.uuid", ondelete="CASCADE"), primary_key=True),
    Column("tag_value", Integer, ForeignKey("tags.value", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Training(Base):
    """
    Таблица тренинга (базового)
    """
    __tablename__ = "trainings"

    uuid: Mapped[UUID4] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    title: Mapped[str] = mapped_column(sa.String(100), nullable=False, comment="Заголовок тренинга")
    description: Mapped[str] = mapped_column(sa.Text, nullable=False, comment="Описание тренинга")
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        comment="id ссылка на создателя"
    )
    level_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("levels.value", ondelete="SET NULL"),
        comment="id ссылка на уровень прохождения тренинга"
    )

    duration_minutes: Mapped[Optional[int]] = mapped_column(
        sa.Integer,
        nullable=True,
        comment="Ожидаемое время прохождения тренинга в минутах"
    )

    publish: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default=sa.false(),
        comment="Опубликован ли тренинг"
    )

    skip_steps: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=True,
        server_default=sa.true(),
        comment="Пропуск шагов"
    )

    created_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime,
        server_default=text("NOW()")
    )

    creator: Mapped["User"] = relationship(
        "backend.models.users.User",
        back_populates="created_trainings"
    )

    steps: Mapped[List["TrainingStep"]] = relationship(
        "backend.models.trainings.TrainingStep",
        back_populates="training",
        order_by="backend.models.trainings.TrainingStep.id",
        cascade="all, delete-orphan",
        lazy="joined",
        passive_deletes=True
    )

    level: Mapped[Optional["Levels"]] = relationship(
        "backend.models.trainings.Levels",
        back_populates="trainings",
        foreign_keys=[level_id]
    )

    tags: Mapped[List["Tags"]] = relationship(
        "backend.models.trainings.Tags",
        secondary=training_tags,
        back_populates="trainings"
    )


class TrainingStep(Base):
    """
    Таблица шага тренинга (базового) с поддержкой вложенности
    """
    __tablename__ = "training_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    training_uuid: Mapped[UUID4] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trainings.uuid", ondelete="CASCADE"),
        nullable=False
    )

    step_number: Mapped[int] = mapped_column(sa.Integer)
    action_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("typesactions.value", ondelete="SET NULL")
    )

    parent_step_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("training_steps.id", ondelete="CASCADE"),
        nullable=True,
        comment="ID родительского шага для вложенной структуры"
    )

    area: Mapped[Optional[Dict]] = mapped_column(JSONB)
    meta: Mapped[Optional[Dict]] = mapped_column(JSONB)
    annotation: Mapped[Optional[str]] = mapped_column(sa.Text)
    image_url: Mapped[Optional[str]] = mapped_column(sa.Text)

    training: Mapped["Training"] = relationship(
        "backend.models.trainings.Training",
        back_populates="steps"
    )

    action_type: Mapped[Optional["TypesAction"]] = relationship(
        "backend.models.trainings.TypesAction",
        back_populates="steps"
    )

    steps: Mapped[List["TrainingStep"]] = relationship(
        "backend.models.trainings.TrainingStep",
        back_populates="parent_step",
        cascade="all, delete-orphan",
        lazy="joined",
        foreign_keys=[parent_step_id]
    )

    parent_step: Mapped[Optional["TrainingStep"]] = relationship(
        "backend.models.trainings.TrainingStep",
        back_populates="steps",
        remote_side=[id],
        foreign_keys=[parent_step_id]
    )


class TypesAction(Base):
    """
    Таблица типов шагов тренинга
    """
    __tablename__ = "typesactions"

    value: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[Optional[str]] = mapped_column(sa.String(50), unique=True)

    steps: Mapped[List["TrainingStep"]] = relationship(
        "backend.models.trainings.TrainingStep",
        back_populates="action_type"
    )


class Tags(Base):
    """
    Таблица тегов тренинга
    """
    __tablename__ = "tags"

    value: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)

    trainings: Mapped[List["Training"]] = relationship(
        "backend.models.trainings.Training",
        secondary=training_tags,
        back_populates="tags"
    )


class Levels(Base):
    """
    Таблица уровней тренинга
    """
    __tablename__ = "levels"

    value: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)

    trainings: Mapped[List["Training"]] = relationship(
        "backend.models.trainings.Training",
        back_populates="level"
    )
