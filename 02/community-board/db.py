from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+psycopg://kks@localhost:5432/community" # postgresql+psycopg://<유저>:<비밀번호>@<호스트>:<포트>/<DB이름>

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """모든 ORM 모델의 super class"""
    pass

def get_db():
    """session 객체 생성 함수"""
    db = session_local()
    try:
        yield db
    finally: # 에러가 발생해도 세션은 닫기
        db.close()