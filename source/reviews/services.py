from source.db.models import Review
from source.auth.services import UserService
from source.books.services import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import ReviewCreateModel
from fastapi import HTTPException, status
from sqlmodel import select, desc

book_service = BookService()
user_service = UserService()

class ReviewService:

    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            user = await user_service.get_user_by_email(email=user_email, session=session)
            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)
            
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
                
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            new_review.user = user
            new_review.book = book
            
            session.add(new_review)
            await session.commit()
            return new_review
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Opps...Something went wrong"
            )
    
    async def get_reviews(self, review_uid:str, session:AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found..."
            )
        return result.first()
    
    async def get_all_reviews(self, session:AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        
        result = await session.exec(statement)
        return result.all()
    
    async def delete_review_to_from_book(self, review_uid:str, user_email:str, session:AsyncSession):
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_reviews(review_uid, session)
        
        print(review)
        
        if not review or review.user_uid != user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete this review"
            )
        await session.delete(review)
        await session.commit()
