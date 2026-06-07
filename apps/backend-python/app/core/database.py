"""数据库配置模块 - SQLAlchemy 异步引擎与会话管理"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖注入

    每个请求使用单一会话，yield 后自动提交。
    异常时自动回滚。

    事务边界说明：
    - 默认行为：get_db 在 yield 后统一 commit()，异常时 rollback()
    - 服务层 flush() 后、commit() 前发生异常，rollback() 会正确回滚
    - 但如果 flush() 后执行了非数据库操作（如调用外部 API），
      这些操作无法回滚，可能导致数据不一致

    建议在需要原子性操作的服务方法中使用嵌套事务：
    ```python
    async def create_user(self, data: UserCreate) -> User:
        async with self.db.begin():
            existing = await self.get_user_by_username(data.username)
            if existing:
                raise ConflictError(f"用户名已存在: {data.username}")
            user = User(...)
            self.db.add(user)
        # 嵌套事务已自动提交，无需再 flush/refresh
        return user
    ```
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """初始化数据库表结构（开发环境使用）
    TODO: 建议使用 Alembic 迁移管理表结构变更
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose()