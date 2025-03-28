import uuid
from datetime import datetime
from sqlalchemy import text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import *
import sqlalchemy as sa


class Training(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(100), unique=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("type_trainings.id"))
    type: Mapped["Type_training"] = relationship("Type_training", back_populates="trainings")
    start_date: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    image_uuid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)


class Type_training(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name_id: Mapped[int] = mapped_column(ForeignKey("name_trainings.id"))
    name_training: Mapped["Name_training"] = relationship("Name_training", back_populates="type_trainings")
    trainings: Mapped[list["Training"]] = relationship("Training", back_populates="type")
    data: Mapped[dict] = mapped_column(JSONB, default=lambda: {})


class Name_training(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True)
    type_trainings: Mapped[list["Type_training"]] = relationship("Type_training", back_populates="name_training")