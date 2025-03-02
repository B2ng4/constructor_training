from datetime import datetime
from typing import List

from pydantic import BaseModel




class Book(BaseModel):
    title: str
    annotation: str
    date_publishing: datetime




