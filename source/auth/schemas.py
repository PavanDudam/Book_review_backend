from pydantic import BaseModel, Field
from source.books.schemas import Book
from source.reviews.schemas import ReviewModel
import uuid
from datetime import datetime
from typing import List
class UserCreate(BaseModel):
    username:str=Field(max_length=20)
    email:str=Field(max_length=40)
    password:str=Field(min_length=6)
    firstname:str
    lastname:str
    

class UserOut(BaseModel):
    uid : uuid.UUID    
    username:str
    email:str
    firstname:str
    lastname:str
    isverified:bool
    password_hash:str=Field(exclude=True)
    created_at : datetime 
    update_at:datetime
    
    
class UserBookModel(UserOut):
    books:List[Book]
    reviews:List[ReviewModel]
    

class UserLogin(BaseModel):
    email:str
    password:str


class EmailModel(BaseModel):
    addresses:List[str]
    
class PasswordResetRequestModel(BaseModel):
    email : str
    
class PasswordRequestConfirmModel(BaseModel):
    new_password:str
    confirm_password:str