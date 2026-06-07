"""班级模型 - 对应 MySQL classes 表"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Class(Base):
    """班级实体 - 对应 classes 表"""

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="机构 ID"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="班级名称"
    )
    grade: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="年级"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="描述"
    )
    teacher_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="教师 ID"
    )
    max_students: Mapped[int] = mapped_column(
        Integer, default=50, comment="最大学生数"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否启用"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    # 关系
    members = relationship("ClassMember", back_populates="class_", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Class(id={self.id}, name={self.name}, grade={self.grade})>"


class ClassMember(Base):
    """班级成员实体 - 对应 class_members 表"""

    __tablename__ = "class_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="班级 ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="用户 ID"
    )
    role: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="角色 (STUDENT/TEACHER)"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="加入时间"
    )

    # 关系
    class_ = relationship("Class", back_populates="members")

    def __repr__(self) -> str:
        return f"<ClassMember(class_id={self.class_id}, user_id={self.user_id})>"