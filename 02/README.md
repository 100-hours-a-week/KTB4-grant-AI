# Community Board

FastAPI + PostgreSQL + Ollama 기반 커뮤니티 게시판. 회원/게시글/댓글 CRUD에 AI 자동 요약을 더한 학습용 프로젝트.

## 구성

- **Backend**: FastAPI (Route–Controller–Service–Repository 구조)
- **DB**: PostgreSQL + SQLAlchemy 2.0
- **AI Serving**: Ollama (`gemma4:e2b`) 로컬 서빙 — 글/댓글 작성·수정 시 자동 요약
- **Frontend**(AI 그대로 작성): Streamlit 기반

## 폴더 구조

```
community-board/
├── main.py                     # FastAPI 앱 진입점
├── db.py                       # Engine / Session / Base
├── models/                     # SQLAlchemy ORM 모델
├── schemas/                    # Pydantic 입출력 스키마
├── routers/                    # URL 분기 (APIRouter)
├── controllers/                # 요청 위임
├── services/                   # 비즈니스 규칙 + AI 요약
├── repositories/               # DB 접근
├── docs/
│   ├── api-design.md           # 엔드포인트 설계
├── core/
│   ├── api-design.md           # 도메인 예외
│   ├── exception_handlers.py   # 전역 핸들러
│   └── middleware.py           # 요청 시간 측정
├── docs/api-design.md          # REST 엔드포인트 설계
└── frontend/app.py             # Streamlit UI
```

## 실행

### 사전 준비

```bash
uv sync

# PostgreSQL 실행 및 DB 생성
brew services start postgresql@18
psql postgres -c "CREATE DATABASE community;"

# Ollama 기반 gemma4:e2b 다운로드 및 실행
ollama pull gemma4:e2b
ollama run gemma4:e2b
```

### 테이블 생성 (최초 1회)

```bash
cd community-board
python -c "from db import Base, engine; import models; Base.metadata.create_all(engine)"
```

### 서버 + 프론트

```bash
# 터미널 1
cd community-board && uvicorn main:app --reload

# 터미널 2
cd community-board && streamlit run frontend/app.py
```

- API 문서(Swagger): http://localhost:8000/docs
- Streamlit UI: http://localhost:8501