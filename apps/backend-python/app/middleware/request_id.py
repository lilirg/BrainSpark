"""Request ID 中间件 - 为每个请求生成唯一追踪 ID"""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求生成并注入 Request ID"""

    async def dispatch(self, request: Request, call_next):
        try:
            request_id = uuid.uuid4().hex[:12]  # 12位十六进制，48位，碰撞概率更低
        except Exception:
            request_id = "unknown"
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def setup_request_id(app: FastAPI) -> None:
    """配置 Request ID 中间件"""
    app.add_middleware(RequestIDMiddleware)