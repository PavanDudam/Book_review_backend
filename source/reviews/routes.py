from fastapi import APIRouter, Depends, status, HTTPException
from source.db.models import User
from .schemas import ReviewCreateModel
from source.db.main import get_sessiion
from source.auth.dependencies import get_current_user
from sqlmodel.ext.asyncio.session import AsyncSession
from .services import ReviewService
from source.auth.dependencies import RoleChecker, get_current_user

review_router = APIRouter()
review_service = ReviewService()
admin_role_checker = Depends(RoleChecker(['admin']))
user_role_checker = Depends(RoleChecker(['user', 'admin']))

@review_router.get("/", dependencies=[user_role_checker])
async def get_all_reviews(session:AsyncSession=Depends(get_sessiion)):
    reviews = await review_service.get_all_reviews(session)
    
    return reviews

@review_router.get("/{review_uid}",dependencies=[user_role_checker])
async def get_review(review_uid:str, session:AsyncSession=Depends(get_sessiion)):
    review = await review_service.get_reviews(review_uid, session)
    if not review:
        return {"message":"Review does not exist..."}
    return review

@review_router.post("/book/{book_uid}")
async def add_review_to_books(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_sessiion),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session,
    )
    
    return new_review

@review_router.delete("/{review_uid}", dependencies=[user_role_checker], status_code=status.HTTP_200_OK)
async def delete_review(review_uid:str, current_user:User=Depends(get_current_user), session:AsyncSession=Depends(get_sessiion)):
    review = await review_service.delete_review_to_from_book(review_uid=review_uid, user_email=current_user.email, session=session)
    
    return {"message":"successfully deleted review"}
    

