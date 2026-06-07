"""用户管理路由 - 对应 Java 的 UserController.java"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import page_response, success
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=dict)
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表（分页）"""
    service = UserService(db)
    users, total = await service.list_users(page=page, size=size)
    return page_response(
        items=[UserResponse.model_validate(u).model_dump() for u in users],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户详情"""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return success(data=UserResponse.model_validate(user).model_dump())


@router.post("", response_model=dict, status_code=201)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """创建用户"""
    service = UserService(db)
    user = await service.create_user(data)
    return success(
        data=UserResponse.model_validate(user).model_dump(),
        message="用户创建成功",
    )


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    service = UserService(db)
    user = await service.update_user(user_id, data)
    return success(
        data=UserResponse.model_validate(user).model_dump(),
        message="用户更新成功",
    )


@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """删除用户"""
    service = UserService(db)
    await service.delete_user(user_id)
    return success(message="用户删除成功")