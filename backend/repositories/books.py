from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.books import Book


from typing import List



class BookRepository:

    def get_books(self) -> List[Book]:
        ...

    def create_book(self) -> Book:
        ...