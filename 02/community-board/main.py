from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import User, Post, Comment


# App instance 생성
app = FastAPI(title="Community API") # title: Swagger 문서 상단에 표시되는 이름

"""사용자"""
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


# 회원 가입
@app.post("/users", response_model=UserResponse, status_code=201) # UserResponse 형태로 반환
def create_user(user: UserCreate, db: Session = Depends(get_db)): # Session: DB에 보낼 변경 사항을 모아두는 임시 작업 공간
    """email, password, nickname을 받아 DB users에 추가
    
    email이 존재하면 에러 발생
    응답은 UserResponse 모양
    """
    # 이메일 중복 확인
    existing = db.execute( # SELECT query 실행
        select(User).where(User.email == user.email)
    ).scalar_one_or_none() # 일치하는 첫번째 값 or None을 반환 
    if existing:
        raise HTTPException(status_code=400, detail="해당 이메일로 가입된 아이디가 존재합니다.")

    # [1. transient(메모리에서의 객체)] 클래스로 막 만든 객체. 세션 & DB 모두 모름.
    new_user = User(
        email = user.email,
        password = user.password,
        nickname = user.nickname,
    )
    # + add [2. pending(추적 시작)] 세션이 new_user를 INSERT할 예정으로 메모리에 들고 있음.
    db.add(new_user) # Session에 new_user 객체 추적 요청
    # + commit [3. persistent] DB에 INSERT
    db.commit() # INSERT query 실행(autocommit=False 때문에 사용)
    db.refresh(new_user) # DB의 id

    return new_user
    
# 사용자 조회
@app.get("/users/{user_id}", response_model=UserResponse, status_code=200)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.get(User, user_id) # users 테이블에서 user_id PK로 조회
    if db_user is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")

    return db_user

# 사용자 정보 수정
@app.patch("/users/{user_id}", response_model=UserResponse, status_code=200)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    updated_user = user.model_dump(exclude_unset=True) # 수정을 요청한 값만 업데이트한 dict
    for key, value in updated_user.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user

# 사용자 정보 삭제
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    db.delete(db_user)
    db.commit()

    return 

"""게시글"""
class PostCreate(BaseModel):
    author_id: int
    title: str
    content: str

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostResponse(BaseModel):
    id: int
    author_id: int
    title: str
    content: str
    summary: str | None = None

# 게시글 생성
@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """author_id, title, content를 받아 posts 테이블에 생성
    
    author_id의 존재 여부 확인
    응답은 PostResponse 모양
    """
    db_user = db.get(User, post.author_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    summary = summarize_text(post.content) # AI 요약

    new_post = Post(
        author_id = post.author_id,
        title = post.title,
        content = post.content,
        summary = summary
    )
    db.add(new_post)
    db.commit() # INSERT
    db.refresh(new_post)
    
    return new_post

# 게시글 전체 조회
@app.get("/posts", response_model=list[PostResponse], status_code=200)
def get_all_posts(db: Session = Depends(get_db)):
    db_posts = db.execute(select(Post)).scalars().all() # 전부 조회
    return db_posts

# 게시글 조회
@app.get("/posts/{post_id}", response_model=PostResponse, status_code=200)
def get_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.get(Post, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    return db_post

# 게시글 수정
@app.patch("/posts/{post_id}", response_model=PostResponse, status_code=200)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.get(Post, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    updated_post = post.model_dump(exclude_unset=True) # 수정을 요청한 값만 업데이트한 dict
    for key, value in updated_post.items():
        setattr(db_post, key, value)

    # content를 수정한 경우에 AI 요약 재생성
    if "content" in updated_post:
        setattr(db_post, "summary", summarize_text(post.content))
    
    db.commit()
    db.refresh(db_post)

    return db_post

# 게시글 삭제
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.get(Post, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    db.delete(db_post)
    db.commit()

    return

"""댓글"""
class CommentCreate(BaseModel):
    author_id: int
    content: str

class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    summary: str | None = None

# 댓글 생성
@app.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    """post_id, author_id, content를 받아 comments 테이블에 추가
    
    post 존재 여부, author 존재 여부 확인
    응답은 CommentResponse 모양
    """
    db_user, db_post = db.get(User, comment.author_id), db.get(Post, post_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    if db_post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    summary = summarize_text(comment.content)
    
    new_comment = Comment(
        post_id = post_id,
        author_id = comment.author_id,
        content = comment.content,
        summary = summary,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

# 댓글 전체 조회
@app.get("/posts/{post_id}/comments", response_model=list[CommentResponse], status_code=200)
def get_all_comments(post_id: int, db: Session = Depends(get_db)):
    db_post = db.get(Post, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    db_comments = db.execute(
        select(Comment).where(Comment.post_id == post_id)
    ).scalars().all()

    return db_comments

# 댓글 조회
@app.get("/posts/{post_id}/comments/{comment_id}", response_model=CommentResponse, status_code=200)
def get_comment(post_id: int, comment_id: int, db: Session = Depends(get_db)):
    db_post, db_comment = db.get(Post, post_id), db.get(Comment, comment_id)
    if db_post is None: # 게시글 존재 여부 확인
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    if db_comment is None: # 댓글 존재 여부 확인
        raise HTTPException(status_code=404, detail="존재하지 않는 댓글입니다.")
    # comment_id가 post_id에 존재 여부 확인
    if db_comment.post_id != post_id:
        raise HTTPException(status_code=404, detail="해당 게시글의 댓글이 아닙니다.")

    return db_comment

# 댓글 삭제
@app.delete("/posts/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(post_id: int, comment_id: int, db: Session = Depends(get_db)):
    db_post, db_comment = db.get(Post, post_id), db.get(Comment, comment_id)
    if db_post is None: # 게시글 존재 여부 확인
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    if db_comment is None: # 댓글 존재 여부 확인
        raise HTTPException(status_code=404, detail="존재하지 않는 댓글입니다.")
    # comment_id가 post_id에 존재 여부 확인
    if db_comment.post_id != post_id:
        raise HTTPException(status_code=404, detail="해당 게시글의 댓글이 아닙니다.")
    
    db.delete(db_comment)
    db.commit()

    return



# AI 요약
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma4:e2b"

def summarize_text(text: str) -> str | None:
    """입력 text를 ollama를 통해 한 문장으로 요악"""
    prompt = f"다음 글을 한국어로 짧게 한 문장으로 요약하고, 요약한 내용만 출력해줘:\n\n{text}"
    try:
        response = httpx.post(
            url = OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60.,
        )
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error 발생: {e}")
        return None