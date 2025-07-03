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

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "9fbcc1f35a50198b623f46e72c4eadc5bf4dbaffe67fa7971e75d452dd3c65a7"
ALGORITHM = "HS256"

router = APIRouter(
    prefix="/api/user",
)


@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db), logger: logging.Logger = Depends(get_auth_logger),
                           request: Request = None):

    # 유저 존재 여부 확인
    user = user_crud.get_user(db, form_data.username)
    
    # 비밀번호 검증 
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 생성 
    data = {
        "sub": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"로그인 성공: {user.username}, IP: {request.client.host if request else 'unknown'}")
    
    # 응답 반환 
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }