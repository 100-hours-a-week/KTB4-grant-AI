from sqlalchemy.orm import Session

from models import Post
from services import summarize_text
from schemas import PostCreate, PostUpdate
from repositories import user as user_repo, post as post_repo
from core.exceptions import UserNotFound, PostNotFound


def register_post(post: PostCreate, db: Session) -> Post | None:
    """게시글 생성"""
    # 규칙: 존재하지 않는 user_id면 None 반환
    db_user = user_repo.find_by_id(post.author_id, db)
    if db_user is None:
        raise UserNotFound
    
    new_post = Post(
        author_id = post.author_id,
        title = post.title,
        content = post.content,
        summary = summarize_text(post.content),
    )
    return post_repo.save(new_post, db)

def get_post_info(post_id: int, db: Session) -> Post | None:
    db_post = post_repo.find_by_id(post_id, db)
    if db_post is None:
        raise PostNotFound
    return db_post

def update_post_info(post_id: int, post: PostUpdate, db: Session) -> Post | None:
    """게시글 정보 수정"""
    # 규칙: post_id가 존재하면 None 반환
    db_post = post_repo.find_by_id(post_id, db)
    if db_post is None:
        raise PostNotFound
    
    updated_post = post.model_dump(exclude_unset=True)
    for key, val in updated_post.items():
        setattr(db_post, key, val)
    if updated_post.get("content"):
        setattr(db_post, "summary", summarize_text(post.content))
    return post_repo.update(db_post, db)

def remove_post(post_id: int, db: Session) -> bool:
    """게시글 삭제"""
    # 규칙: 삭제 성공시 True, 실패시 False 반환
    db_post = post_repo.find_by_id(post_id, db)
    if not db_post:
        raise PostNotFound
    
    post_repo.delete(db_post, db) 
    return True