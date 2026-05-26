from sqlalchemy.orm import Session

from models import Comment
from services import summarize_text
from schemas import CommentCreate
from repositories import user_repo, post_repo, comment_repo
from core.exceptions import UserNotFound, PostNotFound, CommentNotFound, CommentNotInPost

def register_comment(post_id: int, comment: CommentCreate, db: Session) -> Comment | str:
    db_user, db_post = user_repo.find_by_id(comment.author_id, db), post_repo.find_by_id(post_id, db)
    if db_user is None:
        raise UserNotFound
    if db_post is None:
        raise PostNotFound
    
    new_comment = Comment(
        post_id = post_id,
        author_id = comment.author_id,
        content = comment.content,
        summary = summarize_text(comment.content),
    )
    return comment_repo.save(new_comment, db)

def get_comment_info(post_id: int, comment_id: int, db: Session) -> Comment | str:
    db_post, db_comment = post_repo.find_by_id(post_id, db), comment_repo.find_by_id(comment_id, db)
    if db_post is None: # 게시글 존재 여부 확인
        raise PostNotFound
    if db_comment is None: # 댓글 존재 여부 확인
        raise CommentNotFound
    # comment_id가 post_id에 존재 여부 확인
    if db_comment.post_id != post_id:
        raise CommentNotInPost
    return db_comment

def list_comments(post_id: int, db: Session) -> list[Comment] | None:
    db_post = post_repo.find_by_id(post_id, db)
    if db_post is None:
        return None
    return comment_repo.find_all_by_post_id(post_id, db)

def remove_comment(post_id: int, comment_id: int, db: Session) -> bool | str:
    """댓글 삭제"""
    # 규칙: 삭제 성공시 True, 실패시 "post_not_found" | "comment_not_found" | "comment_not_in_post" 반환
    db_post, db_comment = post_repo.find_by_id(post_id, db), comment_repo.find_by_id(comment_id, db)
    if db_post is None:
        raise PostNotFound
    if db_comment is None:
        raise CommentNotFound
    if db_comment.post_id != post_id:
        raise CommentNotInPost
    
    comment_repo.delete(db_comment, db)
    return True