import time
from fastapi import FastAPI, Request


def register_middlewares(app: FastAPI):
    """app에 모든 미들웨어를 등록"""
    @app.middleware("http") # http 요청에 대한 middleware 등록
    async def process_time_middleware(request: Request, call_next): # middleware는 비동기 처리 필요
        """요청 처리에 걸린 시간을 response header에 추가"""
        start = time.time()
        response = await call_next(request)
        process_time = time.time() - start
        response.headers["process-time"] = f"{process_time:.4f}"
        return response