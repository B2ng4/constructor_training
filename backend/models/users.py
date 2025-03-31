from datetime import datetime
from typing import List

from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import *
import sqlalchemy as sa
import asyncio


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_trainings: Mapped[list["Training"]] = relationship(back_populates="creator")
    assigned_trainings: Mapped[list["TrainingAssignment"]] = relationship(
        back_populates="user"
    )


# class Role(Base):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(sa.String(100))
#     users: Mapped[List["User"]] = relationship("User", back_populates="role")
