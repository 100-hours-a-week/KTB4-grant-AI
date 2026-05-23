from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


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


# In-memory 방식
users_db: dict[int, dict] = {}
next_user_id: int = 0

# 회원 가입
@app.post("/users", response_model=UserResponse, status_code=201) # UserResponse 형태로 반환
def create_user(user: UserCreate):
    """email, password, nickname을 받아 users_db에 생성
    
    email이 존재하면 에러 발생, 존재하지 않으면 next_user_id로 id를 부여
    응답은 UserResponse 모양
    """
    global next_user_id

    if any(user_info['email'] == user.email for user_info in users_db.values()):
        raise HTTPException(status_code=400, detail="해당 이메일로 가입된 아이디가 존재합니다.")

    new_user = {
        "id": next_user_id,
        "email": user.email,
        "password": user.password,
        "nickname": user.nickname,
    }
    users_db[next_user_id] = new_user
    next_user_id += 1

    return new_user
    
# 사용자 조회
@app.get("/users/{user_id}", response_model=UserResponse, status_code=200)
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")

    return users_db[user_id]

# 사용자 정보 수정
@app.patch("/users/{user_id}", response_model=UserResponse, status_code=200)
def update_user(user_id: int, user: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    updated_user = user.model_dump(exclude_unset=True) # 수정을 요청한 값만 업데이트한 dict
    for key, val in updated_user.items():
        users_db[user_id][key] = val
    
    return users_db[user_id]

# 사용자 정보 삭제
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    del users_db[user_id]

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

posts_db: dict[int, dict] = {}
next_post_id: int = 0

# 게시글 생성
@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate):
    """author_id, title, content를 받아 posts_db에 생성
    
    author_id의 존재 여부 확인
    응답은 PostResponse 모양
    """
    global next_post_id

    if post.author_id not in users_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    summary = summarize_text(post.content) # AI 요약

    new_post = {
        "id": next_post_id,
        "author_id": post.author_id,
        "title": post.title,
        "content": post.content,
        "summary": summary,
    }
    posts_db[next_post_id] = new_post
    next_post_id += 1
    
    return new_post

# 게시글 전체 조회
@app.get("/posts", response_model=list[PostResponse], status_code=200)
def get_all_posts():
    return list(posts_db.values())

# 게시글 조회
@app.get("/posts/{post_id}", response_model=PostResponse, status_code=200)
def get_post(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    return posts_db[post_id]

# 게시글 수정
@app.patch("/posts/{post_id}", response_model=PostResponse, status_code=200)
def update_post(post_id: int, post: PostUpdate):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    updated_post = post.model_dump(exclude_unset=True) # 수정을 요청한 값만 업데이트한 dict
    for key, value in updated_post.items():
        posts_db[post_id][key] = value
    
    # content를 수정한 경우에 AI 요약 재생성
    if post.content is not None:
        posts_db[post_id]['summary'] = summarize_text(post.content)
    
    return posts_db[post_id]

# 게시글 삭제
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    del posts_db[post_id]

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


comments_db: dict[int, dict] = {}
next_comment_id: int = 0

# 댓글 생성
@app.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
def create_comment(post_id: int, comment: CommentCreate):
    """post_id, author_id, content를 받아 comments_db에 생성
    
    post 존재 여부, author 존재 여부 확인
    응답은 CommentResponse 모양
    """
    global next_comment_id

    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    if comment.author_id not in users_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    
    summary = summarize_text(comment.content)

    new_comment = {
        "id": next_comment_id,
        "post_id": post_id,
        "author_id": comment.author_id,
        "content": comment.content,
        "summary": summary,
    }
    comments_db[next_comment_id] = new_comment
    next_comment_id += 1

    return new_comment

# 댓글 전체 조회
@app.get("/posts/{post_id}/comments", response_model=list[CommentResponse], status_code=200)
def get_all_comments(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    
    comments = [comment_dict for comment_dict in comments_db.values() if comment_dict['post_id'] == post_id]

    return comments

# 댓글 조회
@app.get("/posts/{post_id}/comments/{comment_id}", response_model=CommentResponse, status_code=200)
def get_comment(post_id: int, comment_id: int):
    if post_id not in posts_db: # 게시글 존재 여부 확인
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    if comment_id not in comments_db: # 댓글 존재 여부 확인
        raise HTTPException(status_code=404, detail="존재하지 않는 댓글입니다.")
    # comment_id가 post_id에 존재 여부 확인
    if post_id != comments_db[comment_id]["post_id"]:
        raise HTTPException(status_code=404, detail="해당 게시글의 댓글이 아닙니다.")

    return comments_db[comment_id]

# 댓글 삭제
@app.delete("/posts/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(post_id: int, comment_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
    if comment_id not in comments_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 댓글입니다.")
    # comment_id가 post_id에 존재 여부 확인
    if post_id != comments_db[comment_id]["post_id"]:
        raise HTTPException(status_code=404, detail="해당 게시글의 댓글이 아닙니다.")
    
    del comments_db[comment_id]

    return



# AI 요약
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma4:e2b"

def summarize_text(text: str) -> str:
    """입력 text를 ollama를 통해 한 문장으로 요악"""
    prompt = f"다음 글을 한국어로 짧게 한 문장으로 요약하고, 요약한 내용만 출력해줘:\n\n{text}"
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