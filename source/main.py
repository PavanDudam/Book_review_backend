from fastapi import FastAPI, status
from source.books.routes import book_router
from source.auth.routes import auth_router
from source.reviews.routes import review_router
from contextlib import asynccontextmanager
from source.db.main import init_db
from source.tags.routes import tags_router
from fastapi.responses import JSONResponse
from .errors import register_all_errors
from .middle_ware import register_middleware

@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting...")
    await init_db()
    yield
    print("server has been stopped...")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
)

register_all_errors(app) 
register_middleware(app) 

app.include_router(book_router, tags=["book"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["users"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])
