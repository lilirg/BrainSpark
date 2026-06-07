"""学生档案相关 Pydantic 模型"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StudentProfileUpdate(BaseModel):
    """更新学生档案请求"""

    age: int | None = Field(None, ge=3, le=20, description="年龄")
    grade: str | None = Field(None, max_length=20, description="年级")
    school: str | None = Field(None, max_length=100, description="学校")
    guardian_name: str | None = Field(None, max_length=50, description="监护人姓名")
    guardian_phone: str | None = Field(None, max_length=20, description="监护人电话")
    notes: str | None = Field(None, description="备注")


class StudentProfileResponse(BaseModel):
    """学生档案响应"""

    id: int
    user_id: int
    age: int | None = None
    grade: str | None = None
    school: str | None = None
    guardian_name: str | None = None
    guardian_phone: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GrowthRecord(BaseModel):
    """成长记录"""

    date: str
    radar: dict[str, float]


class StudentGrowthResponse(BaseModel):
    """学生成长趋势响应"""

    user_id: int
    records: list[GrowthRecord]