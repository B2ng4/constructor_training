import uuid
from datetime import datetime
from typing import Optional, List, Dict

from pydantic import UUID4
from sqlalchemy import ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
import sqlalchemy as sa




class ActionType(str, Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    HOVER = "hover"
    DRAG_DROP = "drag_drop"
    KEY_PRESS = "key_press"
    SCROLL = "scroll"


class Training(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(sa.String(100))
    description: Mapped[Optional[str]] = mapped_column(sa.Text)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, default=datetime.now())
    creator: Mapped["User"] = relationship(back_populates="created_trainings")
    steps: Mapped[List["TrainingStep"]] = relationship(
    back_populates = "training",
    order_by = "TrainingStep.id",
    cascade = "all, delete-orphan",
    lazy = "joined"
)


class TrainingStep(Base):
    id: Mapped[int] = mapped_column( primary_key=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    action_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("typesactions.id"))
    area: Mapped[Optional[Dict]] = mapped_column(JSONB)
    meta: Mapped[Optional[Dict]] = mapped_column(JSONB)
    annotation: Mapped[Optional[str]] = mapped_column(sa.Text)
    image_uuid: Mapped[Optional[UUID4]] = mapped_column(UUID, ForeignKey("images.uuid"))
    training: Mapped["Training"] = relationship(back_populates="steps")
    action_type: Mapped["TypesAction"] = relationship(back_populates="steps")
    image: Mapped["Image"] = relationship(back_populates="steps")


class TypesAction(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(sa.String)
    steps: Mapped[List["TrainingStep"]] = relationship(back_populates="action_type")


class Image(Base):
    uuid: Mapped[UUID4] = mapped_column(UUID, primary_key=True)
    url: Mapped[str] = mapped_column(sa.String(50), unique=True)
    steps: Mapped[List["TrainingStep"]] = relationship(back_populates="image")


