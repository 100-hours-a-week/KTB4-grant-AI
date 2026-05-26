from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from schemas import CommentCreate, CommentResponse
from controllers import comment as comment_controller


router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    return comment_controller.create_comment(post_id, comment, db)
    
# 댓글 전체 조회
@router.get("/{post_id}/comments", response_model=list[CommentResponse], status_code=200)
def get_all_comments(post_id: int, db: Session = Depends(get_db)):
    return comment_controller.get_all_comments(post_id, db)

# 댓글 조회
@router.get("/{post_id}/comments/{comment_id}", response_model=CommentResponse, status_code=200)
def get_comment(post_id: int, comment_id: int, db: Session = Depends(get_db)):
    return comment_controller.get_comment(post_id, comment_id, db)

# 댓글 삭제
@router.delete("/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(post_id: int, comment_id: int, db: Session = Depends(get_db)):
    return comment_controller.delete_comment(post_id, comment_id, db)