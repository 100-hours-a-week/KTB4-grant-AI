from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Comment
from schemas import CommentCreate
from services import comment_service


# 댓글 생성
def create_comment(post_id: int, comment: CommentCreate, db: Session) -> Comment:
    """post_id, author_id, content를 받아 comments 테이블에 추가
    
    post 존재 여부, author 존재 여부 확인
    응답은 CommentResponse 모양
    """
    return comment_service.register_comment(post_id, comment, db)

# 댓글 전체 조회
def get_all_comments(post_id: int, db: Session) -> Comment:
    return comment_service.list_comments(post_id, db)

# 댓글 조회
def get_comment(post_id: int, comment_id: int, db: Session) -> Comment:
    return comment_service.get_comment_info(post_id, comment_id, db)

# 댓글 삭제
def delete_comment(post_id: int, comment_id: int, db: Session) -> Comment:
    comment_service.remove_comment(post_id, comment_id, db)