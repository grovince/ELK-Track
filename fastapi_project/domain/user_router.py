from datetime import timedelta, datetime, timezone
from fastapi import Request
import logging
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status
from utils.logger import get_auth_logger
from database import get_db
from domain import user_crud, user_schema
from domain.user_crud import pwd_context
from middleware.rate_limiter import LoginFailLimiter

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "9fbcc1f35a50198b623f46e72c4eadc5bf4dbaffe67fa7971e75d452dd3c65a7"
ALGORITHM = "HS256"

router = APIRouter(
    prefix="/api/user",
)

login_fail_limiter = LoginFailLimiter(max_failures=5, window_seconds=300)

@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    logger: logging.Logger = Depends(get_auth_logger),
    request: Request = None
):
    
    ip = request.client.host if request else 'unknown'
    user_agent = request.headers.get("user-agent", "") if request else ""
    url = str(request.url) if request else ""
    key = f"{ip}:{form_data.username}"

    # 로그인 시도 전, 차단 여부 확인
    if login_fail_limiter.is_limited(key):
                logger.warning({
                    "event": "login_blocked",
                    "ip": ip,
                    "username": form_data.username,
                    "user_agent": user_agent,
                    "url": url,
                    "response_status": 429,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed login attempts. Please try again later.",
                )

    # 유저 존재 여부 확인
    user = user_crud.get_user(db, form_data.username)
    
    # 비밀번호 검증 및 실패 로그 기록
    if not user or not pwd_context.verify(form_data.password, user.password):
        login_fail_limiter.record_failure(key)
        logger.warning({
            "event": "login_failed",
            "ip": ip,
            "username": form_data.username,
            "user_agent": user_agent,
            "url": url,
            "response_status": 401,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 로그인 성공 시 실패 카운트 초기화
    login_fail_limiter.reset(key)

    # JWT 토큰 생성 
    data = {
        "sub": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    logger.info({
        "event": "login_success",
        "ip": ip,
        "username": user.username,
        "user_agent": user_agent,
        "url": url,
        "response_status": 200,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }

