from sqlalchemy import select
from sqlalchemy.orm import Session

from models import User


def find_by_id(user_id: int, db: Session) -> User | None:
    """DB(db)에서 PK(user_id)로 조회"""
    return db.get(User, user_id)

def find_by_email(email: str, db: Session) -> User | None:
    """User 테이블에서 이메일로 조회"""
    return db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

def save(user: User, db: Session) -> User:
    """user 객체 저장"""
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update(user: User, db: Session) -> User:
    """user 변경 사항 저장"""
    db.commit()
    db.refresh(user)
    return user

def delete(user: User, db: Session) -> None:
    """user 삭제"""
    db.delete(user)
    db.commit()
    return