
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# from fastapi import FastAPI, Header, status, HTTPException
# from pydantic import BaseModel
# from typing import List
# app = FastAPI()


# @app.get("/")
# async def read_root():
#     return {"Message": "Hello World!!"}


# @app.get("/greet/{name}")
# async def read_user(name: str) -> dict:
#     return {"Message": f"Hello {name}"}


# @app.get("/get_headers")
# async def get_headers(
#     accept: str = Header(None),
#     content_type: str = Header(None),
#     user_agent: str = Header(None),
#     host: str = Header(None),
# ):
#     request_response = {}
#     request_response["Accept"] = accept
#     request_response["Content-Type"] = content_type
#     request_response["user-Agent"] = user_agent
#     request_response["Host"] = host
#     return request_response


