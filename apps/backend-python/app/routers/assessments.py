"""测评管理路由"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ServiceUnavailableError
from app.core.response import page_response, success
from app.schemas.assessment import (
    AssessmentResultResponse,
    AssessmentTaskCreate,
    AssessmentTaskResponse,
    AssessmentTaskUpdate,
    AssessmentTypeResponse,
)
from app.services.assessment_service import AssessmentService

router = APIRouter()


async def require_today_tasks_feature() -> bool:
    """条件依赖注入：检查今日待测任务功能是否启用"""
    if not settings.ENABLE_TODAY_TASKS:
        raise ServiceUnavailableError(
            "今日待测任务功能未启用，请设置 ENABLE_TODAY_TASKS=true"
        )
    return True


# === 测评类型 ===
@router.get("/types", response_model=dict)
async def list_assessment_types(db: AsyncSession = Depends(get_db)):
    """获取所有测评类型"""
    service = AssessmentService(db)
    types = await service.list_types()
    return success(
        data=[AssessmentTypeResponse.model_validate(t).model_dump() for t in types]
    )


# === 测评任务 ===
@router.get("/tasks", response_model=dict)
async def list_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取测评任务列表（分页）"""
    service = AssessmentService(db)
    tasks, total = await service.list_tasks(page=page, size=size)
    return page_response(
        items=[AssessmentTaskResponse.model_validate(t).model_dump() for t in tasks],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/tasks/today",
    response_model=dict,
    dependencies=[Depends(require_today_tasks_feature)],
)
async def get_today_tasks(db: AsyncSession = Depends(get_db)):
    """获取今日待测任务"""
    service = AssessmentService(db)
    tasks = await service.get_today_tasks(0)  # TODO: 集成认证后传入当前用户 ID
    return success(
        data=[AssessmentTaskResponse.model_validate(t).model_dump() for t in tasks]
    )


@router.get("/tasks/{task_id}", response_model=dict)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """获取测评任务详情"""
    service = AssessmentService(db)
    task = await service.get_task_by_id(task_id)
    return success(data=AssessmentTaskResponse.model_validate(task).model_dump())


@router.post("/tasks", response_model=dict, status_code=201)
async def create_task(
    data: AssessmentTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建测评任务"""
    service = AssessmentService(db)
    task = await service.create_task(data)
    return success(
        data=AssessmentTaskResponse.model_validate(task).model_dump(),
        message="测评任务创建成功",
    )


@router.put("/tasks/{task_id}", response_model=dict)
async def update_task(
    task_id: int,
    data: AssessmentTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新测评任务"""
    service = AssessmentService(db)
    task = await service.update_task(task_id, data)
    return success(
        data=AssessmentTaskResponse.model_validate(task).model_dump(),
        message="测评任务更新成功",
    )


@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """删除测评任务"""
    service = AssessmentService(db)
    await service.delete_task(task_id)
    return success(message="测评任务删除成功")


# === 测评结果 ===
@router.get("/results", response_model=dict)
async def list_results(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取测评结果列表（分页）"""
    service = AssessmentService(db)
    results, total = await service.list_results(page=page, size=size)
    return page_response(
        items=[
            AssessmentResultResponse.model_validate(r).model_dump()
            for r in results
        ],
        total=total,
        page=page,
        size=size,
    )


@router.get("/results/{result_id}", response_model=dict)
async def get_result(result_id: int, db: AsyncSession = Depends(get_db)):
    """获取测评结果详情"""
    service = AssessmentService(db)
    result = await service.get_result_by_id(result_id)
    return success(
        data=AssessmentResultResponse.model_validate(result).model_dump()
    )