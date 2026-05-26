from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from schemas import UserCreate, UserUpdate, UserResponse
from controllers import user as user_controller


router = APIRouter(prefix="/users", tags=["users"]) # tags: Swagger에서의 그룹

@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_controller.create_user(user, db)

@router.get("/{user_id}", response_model=UserResponse, status_code=200)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_controller.get_user(user_id, db)

@router.patch("/{user_id}", response_model=UserResponse, status_code=200)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return user_controller.update_user(user_id, user, db)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_controller.delete_user(user_id, db)