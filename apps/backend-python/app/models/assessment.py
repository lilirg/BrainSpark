"""测评相关模型 - 对应 MySQL assessment 相关表"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssessmentType(Base):
    """测评类型实体 - 对应 assessment_types 表"""

    __tablename__ = "assessment_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="类型编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="类型名称"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="描述"
    )
    cognitive_dimension: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="认知维度"
    )
    duration_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="时长（秒）"
    )
    version: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="版本"
    )
    config: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="配置（JSON）"
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否发布"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )

    def __repr__(self) -> str:
        return f"<AssessmentType(code={self.code}, name={self.name})>"


class AssessmentTask(Base):
    """测评任务实体 - 对应 assessment_tasks 表"""

    __tablename__ = "assessment_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="机构 ID"
    )
    class_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="班级 ID"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="任务标题"
    )
    type_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="测评类型编码"
    )
    config: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="配置（JSON）"
    )
    difficulty: Mapped[int] = mapped_column(
        Integer, default=1, comment="难度"
    )
    duration_min: Mapped[int] = mapped_column(
        Integer, default=10, comment="时长（分钟）"
    )
    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="分配时间"
    )
    start_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="开始时间"
    )
    end_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="结束时间"
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

    def __repr__(self) -> str:
        return f"<AssessmentTask(id={self.id}, title={self.title})>"


class AssessmentResult(Base):
    """测评结果实体 - 对应 assessment_results 表"""

    __tablename__ = "assessment_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="用户 ID"
    )
    task_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="任务 ID"
    )
    type_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="测评类型编码"
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="请求 ID"
    )
    session_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="会话 ID"
    )
    score_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="评分数据（JSON）"
    )
    cognitive_profile: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="认知画像（JSON）"
    )
    ai_recommendations: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="AI 建议（JSON）"
    )
    report_status: Mapped[str] = mapped_column(
        String(20), default="PENDING", comment="报告状态"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="FINISHED", comment="状态"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="开始时间"
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )

    def __repr__(self) -> str:
        return f"<AssessmentResult(id={self.id}, user_id={self.user_id})>"