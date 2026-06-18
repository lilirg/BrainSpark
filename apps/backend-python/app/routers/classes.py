"""班级管理路由"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import page_response, success
from app.schemas.class_ import (
    AddMemberRequest,
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    ClassMemberResponse,
)
from app.services.class_service import ClassService

router = APIRouter()


@router.get("", response_model=dict)
async def list_classes(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取班级列表（分页）"""
    service = ClassService(db)
    classes, total = await service.list_classes(page=page, size=size)
    return page_response(
        items=[ClassResponse.model_validate(c).model_dump() for c in classes],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{class_id}", response_model=dict)
async def get_class(class_id: int, db: AsyncSession = Depends(get_db)):
    """获取班级详情"""
    service = ClassService(db)
    class_ = await service.get_class_by_id(class_id)
    return success(data=ClassResponse.model_validate(class_).model_dump())


@router.post("", response_model=dict, status_code=201)
async def create_class(data: ClassCreate, db: AsyncSession = Depends(get_db)):
    """创建班级"""
    service = ClassService(db)
    class_ = await service.create_class(data)
    return success(
        data=ClassResponse.model_validate(class_).model_dump(),
        message="班级创建成功",
    )


@router.put("/{class_id}", response_model=dict)
async def update_class(
    class_id: int,
    data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新班级信息"""
    service = ClassService(db)
    class_ = await service.update_class(class_id, data)
    return success(
        data=ClassResponse.model_validate(class_).model_dump(),
        message="班级更新成功",
    )


@router.delete("/{class_id}", response_model=dict)
async def delete_class(class_id: int, db: AsyncSession = Depends(get_db)):
    """删除班级"""
    service = ClassService(db)
    await service.delete_class(class_id)
    return success(message="班级删除成功")


@router.get("/{class_id}/members", response_model=dict)
async def list_members(class_id: int, db: AsyncSession = Depends(get_db)):
    """获取班级成员列表"""
    service = ClassService(db)
    members = await service.list_members(class_id)
    return success(
        data=[ClassMemberResponse.model_validate(m).model_dump() for m in members]
    )


@router.post("/{class_id}/members", response_model=dict, status_code=201)
async def add_member(
    class_id: int,
    data: AddMemberRequest,
    db: AsyncSession = Depends(get_db),
):
    """添加班级成员"""
    service = ClassService(db)
    member = await service.add_member(class_id, data)
    return success(
        data=ClassMemberResponse.model_validate(member).model_dump(),
        message="成员添加成功",
    )


@router.delete("/{class_id}/members/{user_id}", response_model=dict)
async def remove_member(
    class_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """移除班级成员"""
    service = ClassService(db)
    await service.remove_member(class_id, user_id)
    return success(message="成员移除成功")