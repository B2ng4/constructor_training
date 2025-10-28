from datetime import datetime
from typing import List, Optional

from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.core.database import Base
import sqlalchemy as sa


class User(Base):
    """
    Таблица пользователя
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(sa.String(15))
    password: Mapped[Optional[str]] = mapped_column(sa.String(100))
    first_name: Mapped[Optional[str]] = mapped_column(sa.String(50))
    last_name: Mapped[Optional[str]] = mapped_column(sa.String(50))
    registration_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime,
        server_default=text("NOW()")
    )
    photo: Mapped[Optional[str]] = mapped_column(sa.String, nullable=True)

    created_trainings: Mapped[List["Training"]] = relationship(
        "backend.models.trainings.Training",
        back_populates="creator"
    )
