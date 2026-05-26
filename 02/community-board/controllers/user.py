from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import User
from schemas import UserCreate, UserUpdate
from services import user_service
from repositories import user_repo


# 회원 가입
def create_user(user: UserCreate, db: Session) -> User: # Session: DB에 보낼 변경 사항을 모아두는 임시 작업 공간
    """email, password, nickname을 받아 DB users에 추가
    
    email이 존재하면 에러 발생
    응답은 UserResponse 모양
    """
    return user_service.register_user(user, db)
    
# 사용자 조회
def get_user(user_id: int, db: Session) -> User:
    return user_service.get_user_info(user_id, db)

# 사용자 정보 수정
def update_user(user_id: int, user: UserUpdate, db: Session) -> User:
    return user_service.update_user_info(user_id, user, db)

# 사용자 정보 삭제
def delete_user(user_id: int, db: Session) -> None:
    user_service.remove_user(user_id, db)