"""班级相关 Pydantic 模型"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ClassCreate(BaseModel):
    """创建班级请求"""

    name: str = Field(..., min_length=1, max_length=100, description="班级名称")
    grade: str | None = Field(None, max_length=20, description="年级")
    description: str | None = Field(None, description="描述")
    teacher_id: int | None = Field(None, description="教师 ID")
    max_students: int = Field(50, ge=1, le=200, description="最大学生数")


class ClassUpdate(BaseModel):
    """更新班级请求"""

    name: str | None = Field(None, min_length=1, max_length=100, description="班级名称")
    grade: str | None = Field(None, max_length=20, description="年级")
    description: str | None = Field(None, description="描述")
    teacher_id: int | None = Field(None, description="教师 ID")
    max_students: int | None = Field(None, ge=1, le=200, description="最大学生数")
    is_active: bool | None = Field(None, description="是否启用")


class ClassResponse(BaseModel):
    """班级响应"""

    id: int
    name: str
    grade: str | None = None
    description: str | None = None
    teacher_id: int | None = None
    max_students: int = 50
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClassMemberResponse(BaseModel):
    """班级成员响应"""

    id: int
    class_id: int
    user_id: int
    role: str | None = None
    joined_at: datetime

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    """添加成员请求"""

    user_id: int = Field(..., description="用户 ID")
    role: str = Field("STUDENT", description="角色 (STUDENT/TEACHER)")