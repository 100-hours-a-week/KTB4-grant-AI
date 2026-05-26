from sqlalchemy import select, Sequence
from sqlalchemy.orm import Session

from models import Post


def find_by_id(post_id: int, db: Session) -> Post | None:
    return db.get(Post, post_id)

def find_all(db: Session) -> Sequence[Post]:
    return db.execute(select(Post)).scalars().all()

def save(post: Post, db: Session) -> Post:
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def update(post: Post, db: Session) -> Post:
    db.commit()
    db.refresh(post)
    return post

def delete(post: Post, db: Session) -> None:
    db.delete(post)
    db.commit()
    return