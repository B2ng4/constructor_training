import uuid
from datetime import datetime
from sqlalchemy import text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import *
import sqlalchemy as sa

from models.users import User


class Training(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    creator: Mapped["User"] = relationship(back_populates="created_trainings")
    steps: Mapped[list["TrainingStep"]] = relationship(back_populates="training", order_by="TrainingStep.step_number")
    assignments: Mapped[list["TrainingAssignment"]] = relationship(back_populates="training")


class TrainingStep(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    step_number: Mapped[int]
    image_url: Mapped[str]
    area: Mapped[dict] = mapped_column(JSON)
    description: Mapped[str]
    training: Mapped["Training"] = relationship(back_populates="steps")


class TrainingAssignment(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assigned_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    training: Mapped["Training"] = relationship(back_populates="assignments")
    user: Mapped["User"] = relationship(back_populates="assigned_trainings")