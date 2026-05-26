from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from schemas import PostCreate, PostUpdate, PostResponse
from controllers import post as post_controller


router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return post_controller.create_post(post, db)

@router.get("", response_model=list[PostResponse], status_code=200)
def get_all_posts(db: Session = Depends(get_db)):
    return post_controller.get_all_posts(db)

@router.get("/{post_id}", response_model=PostResponse, status_code=200)
def get_post(post_id: int, db: Session = Depends(get_db)):
    return post_controller.get_post(post_id, db)

@router.patch("/{post_id}", response_model=PostResponse, status_code=200)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    return post_controller.update_post(post_id, post, db)

@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    return post_controller.delete_post(post_id, db)