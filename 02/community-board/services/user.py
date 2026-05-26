from sqlalchemy.orm import Session

from models import User
from schemas import UserCreate, UserUpdate
from repositories import user as user_repo
from core.exceptions import UserNotFound, EmailAlreadyExists


def register_user(user: UserCreate, db: Session) -> User | None:
    """회원가입"""
    # 규칙: 같은 이메일이 있으면 None 반환
    db_user = user_repo.find_by_email(user.email, db)
    if db_user is not None:
        raise EmailAlreadyExists
    
    new_user = User(
        email = user.email,
        password = user.password,
        nickname = user.nickname,
    )
    return user_repo.save(new_user, db)

def get_user_info(user_id: int, db: Session) -> User | None:
    db_user = user_repo.find_by_id(user_id, db)
    if db_user is None:
        raise UserNotFound
    return db_user

def update_user_info(user_id: int, user: UserUpdate, db: Session) -> User | None:
    """사용자 정보 수정"""
    # 규칙: user_id가 존재하면 None 반환
    db_user = user_repo.find_by_id(user_id, db)
    if db_user is None:
        raise UserNotFound
    
    updated_user = user.model_dump(exclude_unset=True)
    for key, val in updated_user.items():
        setattr(db_user, key, val)
    return user_repo.update(db_user, db)

def remove_user(user_id: int, db: Session) -> None:
    """사용자 삭제"""
    # 규칙: 삭제 성공시 True, 실패시 False 반환
    db_user = user_repo.find_by_id(user_id, db)
    if db_user is None:
        raise UserNotFound
    user_repo.delete(db_user, db)
    return True