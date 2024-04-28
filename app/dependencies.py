from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from cachetools import TTLCache

from app.services.user_service import get_user
from app.schemas.user import UserResponse
from app.utils.auth import check_login_base
from app.utils.database import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建一个缓存，设置最大缓存数量和过期时间（单位：秒）
token_cache = TTLCache(maxsize=1000, ttl=3600)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 检查 token 是否在缓存中
    if token in token_cache:
        user = token_cache[token]
    else:
        # 向 OA 服务器发送请求验证 token
        user_info = check_login_base(token)
        
        if user_info is None:
            raise credentials_exception
        user = get_user(db, user_info)
        # 将验证后的用户信息存入缓存
        token_cache[token] = user
    
    return user

def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_permission(current_user: UserResponse = Depends(get_current_user)) -> bool:
    if current_user is None or not current_user.is_active:
        return False
    return True