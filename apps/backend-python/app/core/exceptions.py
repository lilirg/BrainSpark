"""自定义异常模块"""

from __future__ import annotations

from typing import Any


class BrainSparkException(Exception):
    """业务异常基类"""

    def __init__(
        self,
        code: int = 400,
        message: str = "请求失败",
        data: Any = None,
        errors: list[dict[str, str]] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.data = data
        self.errors = errors or []
        super().__init__(self.message)


class NotFoundError(BrainSparkException):
    """资源未找到异常"""

    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(code=404, message=message)


class ValidationError(BrainSparkException):
    """参数校验异常"""

    def __init__(self, message: str = "参数校验失败", errors: list[dict[str, str]] | None = None) -> None:
        super().__init__(code=422, message=message, errors=errors)


class UnauthorizedError(BrainSparkException):
    """未授权异常"""

    def __init__(self, message: str = "未授权访问") -> None:
        super().__init__(code=401, message=message)


class ForbiddenError(BrainSparkException):
    """禁止访问异常"""

    def __init__(self, message: str = "无权限访问") -> None:
        super().__init__(code=403, message=message)


class ConflictError(BrainSparkException):
    """资源冲突异常"""

    def __init__(self, message: str = "资源已存在") -> None:
        super().__init__(code=409, message=message)


class ServiceUnavailableError(BrainSparkException):
    """服务不可用异常"""

    def __init__(self, message: str = "服务暂不可用") -> None:
        super().__init__(code=503, message=message)