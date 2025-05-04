import uuid
from datetime import datetime
from typing import Optional, List, Dict

from pydantic import UUID4
from sqlalchemy import ForeignKey, JSON, Enum, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
import sqlalchemy as sa


class Training(Base):
    __tablename__ = "trainings"
    uuid: Mapped[UUID4] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    title: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime, server_default=text("NOW()"),
    )
    creator: Mapped["User"] = relationship(back_populates="created_trainings")
    steps: Mapped[List["TrainingStep"]] = relationship(
        back_populates="training",
        order_by="TrainingStep.id",
        cascade="all, delete-orphan",
        lazy="joined",
        passive_deletes=True
    )


class TrainingStep(Base):
    __tablename__ = "training_steps"
    id: Mapped[int] = mapped_column(primary_key=True)
    training_uuid: Mapped[UUID4] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trainings.uuid", ondelete="CASCADE"),
        nullable=False
    )
    step_number: Mapped[int] = mapped_column(sa.Integer)
    action_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("typesactions.id", ondelete="SET NULL")
    )
    area: Mapped[Optional[Dict]] = mapped_column(JSONB)
    meta: Mapped[Optional[Dict]] = mapped_column(JSONB)
    annotation: Mapped[Optional[str]] = mapped_column(sa.Text)
    image_url: Mapped[Optional[str]] = mapped_column(sa.Text)
    training: Mapped["Training"] = relationship(back_populates="steps")
    action_type: Mapped["TypesAction"] = relationship(back_populates="steps")


class TypesAction(Base):
    __tablename__ = "typesactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(sa.String(50), unique=True)
    steps: Mapped[List["TrainingStep"]] = relationship(
        back_populates="action_type",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
