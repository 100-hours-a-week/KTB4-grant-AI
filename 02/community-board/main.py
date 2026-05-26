from fastapi import FastAPI

from routers import user_router, post_router, comment_router
from core.exception_handlers import register_exception_handlers
from core.middleware import register_middlewares


# App instance 생성
app = FastAPI(title="Community API") # title: Swagger 문서 상단에 표시되는 이름

# Router
app.include_router(user_router) # 사용자
app.include_router(post_router) # 게시글
app.include_router(comment_router) # 댓글

# Exception handler
register_exception_handlers(app)

# Middleware
register_middlewares(app)