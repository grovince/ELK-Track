from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user_schema import UserCreate
from models import User

# bcrypt 해시 알고리즘으로 비밀번호를 안전하게 저장 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 새로운 유저를 DB에 저장 
def create_user(db: Session, user_create: UserCreate):
    db_user = User(username=user_create.username,
                   password=pwd_context.hash(user_create.password1))
    db.add(db_user)
    db.commit()

# 유저 존재 유무 확인
def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username)
    ).first()

# 유저 정보 얻기 
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()