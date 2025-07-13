from pydantic import BaseModel
from typing import List
import uuid
from source.reviews.schemas import ReviewModel
from datetime import datetime, date
from source.tags.schemas import TagModel

class Book(BaseModel):
    uid:uuid.UUID
    title:str
    author:str
    publisher:str
    published_date:date
    page_count:int
    language:str
    created_at:datetime
    update_at:datetime
    
class BookDetailModel(Book):
    reviews: List[ReviewModel]
    tags:List[TagModel]

    
class BookCreateModel(BaseModel):
    title:str
    author:str
    publisher:str
    published_date:str
    page_count:int
    language:str
    
class BookUpdateModel(BaseModel):
    title:str
    author:str
    publisher:str
    page_count:int
    language:str
    
