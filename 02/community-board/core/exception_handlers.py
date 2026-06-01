"""앱 전반에서 발생하는 예외를 가로채어 정해진 형식의 응답으로 변환하는 전역 처리기로, 에러 처리를 router나 controller에서 개별적으로 처리하지 않고 전역에서 통일.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import (
    UserNotFound, EmailAlreadyExists,
    PostNotFound,
    CommentNotFound, CommentNotInPost
)


def register_exception_handlers(app: FastAPI):
    """앱에 모든 exception handler들을 등록하는 함수"""
    # ----- 도메인 예외들 ----- #
    @app.exception_handler(UserNotFound)
    async def user_not_found(request: Request, exc: UserNotFound):
        return JSONResponse(content={"detail": "존재하지 않는 사용자입니다."}, status_code=404)
    
    @app.exception_handler(EmailAlreadyExists)
    async def email_already_exists(request: Request, exc: EmailAlreadyExists):
        return JSONResponse(content={"detail": "해당 이메일로 가입된 아이디가 존재합니다."}, status_code=400)

    @app.exception_handler(PostNotFound)
    async def post_not_found(request: Request, exc: PostNotFound):
        return JSONResponse(content={"detail": "존재하지 않는 게시글입니다."}, status_code=404)
    
    @app.exception_handler(CommentNotFound)
    async def comment_not_found(request: Request, exc: CommentNotFound):
        return JSONResponse(content={"detail": "존재하지 않는 댓글입니다."}, status_code=404)
    
    @app.exception_handler(CommentNotInPost)
    async def comment_not_in_post(request: Request, exc: CommentNotInPost):
        return JSONResponse(content={"detail": "해당 게시글의 댓글이 아닙니다."})
    
    # ----- FastAPI 공통 예외들 -----
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        """입력 검증 실패(422, 400)"""
        return JSONResponse(
            content={"detail": "올바르지 않은 요청입니다.", "errors": exc.errors()},
            status_code=400,
        )
    
    # ----- 남은 모든 예외 처리 -----
    @app.exception_handler(Exception)
    async def server_error(request: Request, exc: Exception):
        """남은 예외 처리(서버 에러 등)"""
        return JSONResponse(
            content={"detail": "서버 내부 오류입니다."},
            status_code=500
        )