"""统一响应格式模块"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""

    code: int = 200
    message: str = "ok"
    data: T | None = None
    trace_id: str = ""


class PageData(BaseModel, Generic[T]):
    """分页数据"""

    items: list[T]
    total: int
    page: int = 1
    size: int = 20


class PageResponse(BaseModel, Generic[T]):
    """统一分页响应"""

    code: int = 200
    message: str = "ok"
    data: PageData[T]
    trace_id: str = ""


def success(data: Any = None, message: str = "ok") -> ApiResponse:
    """成功响应"""
    return ApiResponse(code=200, message=message, data=data)


def page_response(
    items: list[Any],
    total: int,
    page: int = 1,
    size: int = 20,
) -> PageResponse:
    """分页响应"""
    return PageResponse(
        code=200,
        message="ok",
        data=PageData(items=items, total=total, page=page, size=size),
    )