"""测评相关 Pydantic 模型"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# === 测评类型 ===
class AssessmentTypeResponse(BaseModel):
    """测评类型响应"""

    id: int
    code: str
    name: str
    description: str | None = None
    cognitive_dimension: str | None = None
    duration_seconds: int | None = None
    version: str | None = None
    is_published: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# === 测评任务 ===
class AssessmentTaskCreate(BaseModel):
    """创建测评任务请求"""

    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    type_code: str = Field(..., description="测评类型编码")
    class_id: int | None = Field(None, description="班级 ID")
    difficulty: int = Field(1, ge=1, le=10, description="难度")
    duration_min: int = Field(10, ge=1, le=120, description="时长（分钟）")
    start_at: datetime | None = Field(None, description="开始时间")
    end_at: datetime | None = Field(None, description="结束时间")


class AssessmentTaskUpdate(BaseModel):
    """更新测评任务请求"""

    title: str | None = Field(None, min_length=1, max_length=200, description="任务标题")
    difficulty: int | None = Field(None, ge=1, le=10, description="难度")
    duration_min: int | None = Field(None, ge=1, le=120, description="时长（分钟）")
    start_at: datetime | None = Field(None, description="开始时间")
    end_at: datetime | None = Field(None, description="结束时间")
    is_active: bool | None = Field(None, description="是否启用")


class AssessmentTaskResponse(BaseModel):
    """测评任务响应"""

    id: int
    title: str
    type_code: str
    class_id: int | None = None
    difficulty: int = 1
    duration_min: int = 10
    start_at: datetime | None = None
    end_at: datetime | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# === 测评结果 ===
class AssessmentResultResponse(BaseModel):
    """测评结果响应"""

    id: int
    user_id: int
    task_id: int | None = None
    type_code: str
    score_data: dict | None = None
    cognitive_profile: dict | None = None
    report_status: str = "PENDING"
    status: str = "FINISHED"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}