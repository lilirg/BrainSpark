"""日志配置模块"""

from __future__ import annotations

import sys

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """配置日志系统"""
    logger.remove()  # 移除默认处理器

    # 添加控制台处理器
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        colorize=True,
    )

    # 添加文件处理器（生产环境）
    if settings.ENV == "prod":
        logger.add(
            "logs/brainspark-{time:YYYY-MM-DD}.log",
            level="INFO",
            format=settings.LOG_FORMAT,
            rotation="1 day",
            retention="30 days",
            compression="gz",
        )


# 导出预配置的 logger 实例
__all__ = ["logger", "setup_logging"]