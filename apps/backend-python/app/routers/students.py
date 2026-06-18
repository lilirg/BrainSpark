"""学生档案路由"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.schemas.student import (
    StudentGrowthResponse,
    StudentProfileResponse,
    StudentProfileUpdate,
)
from app.services.student_service import StudentService

router = APIRouter()


@router.get("/{user_id}", response_model=dict)
async def get_student_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取学生档案详情"""
    service = StudentService(db)
    profile = await service.get_profile(user_id)
    return success(
        data=StudentProfileResponse.model_validate(profile).model_dump()
    )


@router.put("/{user_id}/profile", response_model=dict)
async def update_student_profile(
    user_id: int,
    data: StudentProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新学生档案"""
    service = StudentService(db)
    profile = await service.create_or_update_profile(user_id, data)
    return success(
        data=StudentProfileResponse.model_validate(profile).model_dump(),
        message="档案更新成功",
    )


@router.get("/{user_id}/growth", response_model=dict)
async def get_student_growth(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取学生成长趋势数据"""
    service = StudentService(db)
    records = await service.get_growth_trend(user_id)
    return success(
        data=StudentGrowthResponse(
            user_id=user_id,
            records=[r.model_dump() for r in records],
        ).model_dump()
    )