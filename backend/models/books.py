from datetime import datetime

from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa
from core.database import *



class Book(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(100))
    annotation: Mapped[str] = mapped_column(sa.Text)
    date_publishing: Mapped[datetime] = mapped_column(sa.DateTime)
