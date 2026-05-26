from pydantic import BaseModel


# 회원 가입 요청 본문
class UserCreate(BaseModel):
    email: str
    password: str
    nickname: str

# 사용자 정보 수정 본문
class UserUpdate(BaseModel):
    # 부분 수정을 위해 None 허용
    password: str | None = None
    nickname: str | None = None

# 사용자 응답 본문
class UserResponse(BaseModel):
    # password 반환 제외
    id: int # 내부 ID
    email: str
    nickname: str