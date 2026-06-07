"""用户模型 - 对应 MySQL users 表"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""

    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    OPERATOR = "OPERATOR"


class User(Base):
    """用户实体 - 对应 users 表"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码（哈希后）"
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, comment="角色"
    )
    real_name: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="真实姓名"
    )
    avatar: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="头像 URL"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"