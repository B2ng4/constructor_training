from datetime import datetime
from typing import List, Optional

from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import *
import sqlalchemy as sa
import asyncio

from models.trainings import Training


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(sa.String(15))
    password: Mapped[Optional[str]] = mapped_column(sa.String(100))
    first_name: Mapped[Optional[str]] = mapped_column(sa.String(50))
    last_name: Mapped[Optional[str]] = mapped_column(sa.String(50))
    registration_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime, default=datetime.now()
    )
    photo: Mapped[Optional[str]] = mapped_column(sa.String, nullable=True)
    created_trainings: Mapped[List["Training"]] = relationship(back_populates="creator")
