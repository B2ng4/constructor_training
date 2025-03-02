from typing import List

from fastapi import APIRouter, Depends
from backend.schemas.books import Book
from backend.depends import get_book_service
from backend.services.books import BookService

router = APIRouter(prefix="/books", tags=["Книги"])



@router.get(
    "",
    responses={400: {"description": "Bad request"}},
    response_model=List[Book],
    description="Получение листинга всех книг",
)

async def получение_списка_книг(
        book_service: BookService = Depends(get_book_service),
        ) -> List[Book]:
        books = book_service.get_books()
        return books


@router.post(
    "",
    responses={400: {"description": "Bad request"}},
    description="Получение листинга всех книг",
)

async def публикация_книги(book_data: Book, book_service: BookService = Depends(get_book_service)) -> List[Book]:
        books = book_service.create_book()
        return books
