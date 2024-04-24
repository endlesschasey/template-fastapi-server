from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.models.table import User
from app.services.user_service import *
from app.schemas.user import *
from app.dependencies import *


router = APIRouter()

@router.post("/loginOA", response_model=UserResponse)
def loginOA(user: UserResponse = Depends(get_current_active_user)):
    return user
