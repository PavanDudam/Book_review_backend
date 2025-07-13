from fastapi import APIRouter, status, Depends
from .schemas import Book, BookUpdateModel, BookCreateModel, BookDetailModel
from fastapi.exceptions import HTTPException
from typing import List
from source.db.main import get_sessiion
from sqlmodel.ext.asyncio.session import AsyncSession
from source.books.services import BookService
from uuid import UUID
from source.auth.dependencies import AccessTokenBearer
from source.auth.dependencies import RoleChecker
from source.errors import BookNotFound

role_checker = Depends(RoleChecker(["admin", "user"]))
book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@book_router.get("/books", response_model=List[Book])
async def get_all_books(
    session: AsyncSession = Depends(get_sessiion),
    token_details: dict = role_checker,
):
    books = await book_service.get_all_books(session)
    return books


@book_router.get("/books/{user_uid}", response_model=List[Book])
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_sessiion),
    token_details: dict = role_checker,
):
    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.post(
    "/books",
    status_code=status.HTTP_200_OK,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_sessiion),
    token_details: dict = Depends(access_token_bearer),
):
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session)
    return new_book


@book_router.get(
    "/book/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_one_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_sessiion),
    token_details: dict = Depends(access_token_bearer),
):
    book = await book_service.get_book(book_uid, session)

    if book:
        return book
    else:
        raise BookNotFound()


@book_router.patch("/book/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_sessiion),
    token_details: dict = Depends(access_token_bearer),
):
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if updated_book:
        return updated_book
    else:
        raise BookNotFound()


@book_router.delete("/book/{book_uid}", dependencies=[role_checker])
async def delete_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_sessiion),
    token_details: dict = Depends(access_token_bearer),
):
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete:
        return {"message": "Successfully deleted book"}
    else:
        raise BookNotFound()