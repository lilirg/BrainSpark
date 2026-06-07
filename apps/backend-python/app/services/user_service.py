"""用户服务 - 对应 Java 的 UserService.java"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import hash_password


class UserService:
    """用户管理服务"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_users(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[User], int]:
        """获取用户列表（分页）"""
        # 查询总数
        count_result = await self.db.execute(
            select(func.count()).select_from(User)
        )
        total = count_result.scalar()

        # 分页查询
        offset = (page - 1) * size
        result = await self.db.execute(
            select(User).offset(offset).limit(size)
        )
        users = list(result.scalars().all())
        return users, total

    async def get_user_by_id(self, user_id: int) -> User:
        """根据 ID 获取用户"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError(f"用户不存在: id={user_id}")
        return user

    async def get_user_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing = await self.get_user_by_username(data.username)
        if existing:
            raise ConflictError(f"用户名已存在: {data.username}")

        # 创建用户（密码在服务层哈希）
        user = User(
            username=data.username,
            password=hash_password(data.password),
            role=data.role,
            real_name=data.real_name,
            avatar=data.avatar,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        """更新用户信息"""
        user = await self.get_user_by_id(user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        """删除用户"""
        user = await self.get_user_by_id(user_id)
        await self.db.delete(user)
        await self.db.flush()