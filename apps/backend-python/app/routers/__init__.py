"""路由注册模块"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.routers import assessments, auth, classes, students, users
from app.services.auth_service import get_current_user

api_router = APIRouter()

# 认证路由保持公开（登录、注册、刷新令牌不需要认证）
api_router.include_router(auth.router, prefix="/auth", tags=["认证管理"])

# 以下路由需要认证
api_router.include_router(
    users.router, prefix="/users", tags=["用户管理"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    classes.router, prefix="/classes", tags=["班级管理"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    students.router, prefix="/students", tags=["学生档案"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    assessments.router, prefix="/assessments", tags=["测评管理"],
    dependencies=[Depends(get_current_user)],
)