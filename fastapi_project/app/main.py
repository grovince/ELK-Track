from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime
import logging, os
from domain import user_router
from utils.logger import get_access_logger

app = FastAPI()

origins = [
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

app.include_router(user_router.router)

access_logger = get_access_logger()

@app.middleware("http")
async def log_request_info(request: Request, call_next):
    log_data = {
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "access_time": datetime.now().isoformat(),
        "url": str(request.url)
    }
    access_logger.info(log_data)
    response = await call_next(request)
    return response