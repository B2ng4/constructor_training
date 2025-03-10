from datetime import datetime

from sqlalchemy import text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import *
import sqlalchemy as sa


class Event(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(100), unique=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("type_events.id"))
    type: Mapped["Type_event"] = relationship("Type_event", back_populates="events")
    start_date: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)


class Type_event(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(ForeignKey("name_events.id"))
    name_event: Mapped["Name_event"] = relationship("Name_event", back_populates="type_events")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="type")
    data: Mapped[dict] = mapped_column(JSONB)


class Name_event(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True)
    type_events: Mapped[list["Type_event"]] = relationship("Type_event", back_populates="name_event")