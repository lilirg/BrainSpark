"""全局异常处理器"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.core.exceptions import BrainSparkException
from app.core.logging import logger
from app.core.response import ApiResponse


def setup_error_handlers(app: FastAPI) -> None:
    """配置全局异常处理器"""

    @app.exception_handler(BrainSparkException)
    async def brainspark_exception_handler(
        request: Request,
        exc: BrainSparkException,
    ) -> JSONResponse:
        """处理业务异常"""
        trace_id = getattr(request.state, "request_id", "")
        logger.warning(
            f"业务异常 | trace_id={trace_id} | code={exc.code} | message={exc.message}"
        )
        return JSONResponse(
            status_code=exc.code,
            content=ApiResponse(
                code=exc.code,
                message=exc.message,
                data=exc.data,
                trace_id=trace_id,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """处理参数校验异常"""
        trace_id = getattr(request.state, "request_id", "")
        errors = [
            {"field": ".".join(str(x) for x in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        logger.warning(
            f"参数校验失败 | trace_id={trace_id} | errors={errors}"
        )
        return JSONResponse(
            status_code=422,
            content=ApiResponse(
                code=422,
                message="参数校验失败",
                data=None,
                trace_id=trace_id,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """处理未预期的全局异常"""
        trace_id = getattr(request.state, "request_id", "")
        logger.error(
            f"未预期异常 | trace_id={trace_id} | error={str(exc)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content=ApiResponse(
                code=500,
                message="服务器内部错误",
                data=None,
                trace_id=trace_id,
            ).model_dump(),
        )