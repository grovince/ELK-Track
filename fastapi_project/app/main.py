from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime
from domain import user_router
from utils.logger import get_access_logger
from middleware.rate_limiter import RateLimiter

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

@app.get("/test")
async def test_endpoint():
    return {"message": "test page"}

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

app.middleware("http")(RateLimiter(requests_per_minute=10)) # IP별 요청 횟수 측정 기능 미들웨어 등록