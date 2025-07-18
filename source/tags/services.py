from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from source.books.services import BookService
from source.db.models import Tag

from .schemas import TagAddModel, TagCreateModel
from source.errors import BookNotFound, TagNotFound, TagAlreadyExists

book_service = BookService()


class TagService:
    async def get_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))
        result = await session.exec(statement)
        return result.all()

    async def add_tag_to_book(
        self, book_uid: str, tag_data: TagAddModel, session: AsyncSession
    ):
        book = await book_service.get_book(book_uid=book_uid, session=session)

        if not book:
            raise BookNotFound()

        for tag_item in tag_data.tags:
            statement = select(Tag).where(Tag.name == tag_item.name)
            result = await session.exec(statement)
            tag = result.one_or_none()
            if not tag:
                tag = Tag(name=tag_item.name)

            book.tags.append(tag)

        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.exec(statement)

        return result.first()

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        statement = select(Tag).where(Tag.name == tag_data.name)

        result = await session.exec(statement)
        tag = result.first()

        if tag:
            raise TagAlreadyExists()
        new_tag = Tag(name=tag_data.name)
        session.add(new_tag)
        await session.commit()
        return new_tag

    async def update_tag(self, tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid=tag_uid, session=session)

        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        update_data_dict = tag_update_data.model_dump(exclude_unset=True)

        for k, v in update_data_dict.items():
            if hasattr(tag, k):
                setattr(tag, k, v)

        await session.commit()
        await session.refresh(tag)
        return tag

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFound()

        await session.delete(tag)
        await session.commit()
