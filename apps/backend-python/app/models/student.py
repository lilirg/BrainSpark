"""学生档案模型 - 对应 MySQL students 表"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudentProfile(Base):
    """学生档案实体 - 对应 student_profiles 表"""

    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False, comment="用户 ID"
    )
    age: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="年龄"
    )
    grade: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="年级"
    )
    school: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="学校"
    )
    guardian_name: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="监护人姓名"
    )
    guardian_phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="监护人电话"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="备注"
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

    def __repr__(self) -> str:
        return f"<StudentProfile(user_id={self.user_id}, grade={self.grade})>"