"""BrainSpark 业务后端服务入口

启动命令:
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.logging import logger, setup_logging
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.request_id import setup_request_id
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    setup_logging()
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    logger.info(f"🌐 环境: {settings.ENV}")
    logger.info(f"🗄️  数据库: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # 验证配置（在启动时而非导入时验证，提供更友好的错误信息）
    try:
        settings.validate()
        logger.info("✅ 配置验证通过")
    except ValueError as e:
        logger.error(f"❌ 配置验证失败: {e}")
        raise

    if settings.ENV == "dev":
        logger.info("ℹ️  开发环境：请使用 'alembic upgrade head' 初始化数据库表结构")
        logger.info("ℹ️  如需自动建表，请取消注释下方 init_db() 调用")
        # await init_db()
        # logger.info("✅ 数据库表结构初始化完成")

    yield

    # 关闭时
    await close_db()
    logger.info("👋 服务已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="BrainSpark 业务后端服务 - Python FastAPI 实现",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENV == "dev" else None,
    redoc_url="/redoc" if settings.ENV == "dev" else None,
)

# 配置中间件
setup_cors(app)
setup_request_id(app)

# 配置异常处理器
setup_error_handlers(app)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": settings.APP_VERSION}