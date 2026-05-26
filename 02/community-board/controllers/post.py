from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Post
from schemas import PostCreate, PostUpdate
from services import post_service
from repositories import post_repo


# 게시글 생성
def create_post(post: PostCreate, db: Session) -> Post:
    """author_id, title, content를 받아 posts 테이블에 생성
    
    author_id의 존재 여부 확인
    응답은 PostResponse 모양
    """
    db_user = post_service.register_post(post, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    return db_user

# 게시글 전체 조회
def get_all_posts(db: Session):
    return post_repo.find_all(db)

# 게시글 조회
def get_post(post_id: int, db: Session):
    db_post = post_service.get_post_info(post_id, db)
    if db_post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    return db_post

# 게시글 수정
def update_post(post_id: int, post: PostUpdate, db: Session):
    db_post = post_service.update_post_info(post_id, post, db)
    if db_post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    return db_post

# 게시글 삭제
def delete_post(post_id: int, db: Session):
    if not post_service.remove_post(post_id, db):
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
