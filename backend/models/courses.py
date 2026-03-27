from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
from pydantic import UUID4
from sqlalchemy import Column, ForeignKey, Integer, Table, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

course_trainings = Table(
    "course_trainings",
    Base.metadata,
    Column(
        "course_id",
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "training_uuid",
        UUID(as_uuid=True),
        ForeignKey("trainings.uuid", ondelete="CASCADE"),
        primary_key=True,
    ),
    extend_existing=True,
)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        sa.String(150), nullable=False, comment="Название курса"
    )
    description: Mapped[Optional[str]] = mapped_column(
        sa.Text, nullable=True, comment="Описание курса"
    )
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime, server_default=text("NOW()")
    )

    creator: Mapped["User"] = relationship("models.users.User", lazy="selectin")

    trainings: Mapped[List["Training"]] = relationship(
        "models.trainings.Training",
        secondary=course_trainings,
        lazy="selectin",
    )
