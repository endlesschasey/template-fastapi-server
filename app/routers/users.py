from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.table import User
from app.services.user_service import *
from app.schemas.user import *
from app.dependencies import *
from typing import List
from fastapi import HTTPException

router = APIRouter()

@router.post("/loginOA",response_model=UserResponse)
def loginOA(user: UserResponse = Depends(get_current_active_user)):
    return user


@router.get("/users", response_model=List[UserResponse])
def get_users(permission: bool = Depends(get_current_active_permission), db: Session = Depends(get_db)):
    if permission:
        users = db.query(User).all()
        return [UserResponse.model_validate(user) for user in users]
    
    raise HTTPException(status_code=403, detail="Permission denied")