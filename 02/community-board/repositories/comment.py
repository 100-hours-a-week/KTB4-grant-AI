from sqlalchemy import select, Sequence
from sqlalchemy.orm import Session

from models import Comment


def find_by_id(comment_id: int, db: Session) -> Comment | None:
    return db.get(Comment, comment_id)

def find_all_by_post_id(post_id: int, db: Session) -> Sequence[Comment]:
    return db.execute(
        select(Comment).where(Comment.post_id == post_id)
    ).scalars().all()

def save(comment: Comment, db: Session) -> Comment:
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def delete(comment: Comment, db: Session) -> None:
    db.delete(comment)
    db.commit()
    return