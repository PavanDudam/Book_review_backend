from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        print("before time: ", start_time)

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = (
            f"{request.client.host}:{request.client.port} {request.method} - {request.url.path} - {response.status_code} - completed after {processing_time}"
        )
        print(message)
        return response
    
    
