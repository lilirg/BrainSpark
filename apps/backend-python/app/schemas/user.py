"""用户相关 Pydantic 模型"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """创建用户请求"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: UserRole = Field(..., description="用户角色")
    real_name: str | None = Field(None, max_length=50, description="真实姓名")
    avatar: str | None = Field(None, max_length=255, description="头像 URL")


class UserUpdate(BaseModel):
    """更新用户请求"""

    username: str | None = Field(None, min_length=3, max_length=50, description="用户名")
    real_name: str | None = Field(None, max_length=50, description="真实姓名")
    role: UserRole | None = Field(None, description="用户角色")
    avatar: str | None = Field(None, max_length=255, description="头像 URL")


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    role: UserRole
    real_name: str | None = None
    avatar: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """用户登录请求"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserLoginResponse(BaseModel):
    """用户登录响应"""

    access_token: str
    refresh_token: str
    expires_in: int
    role: UserRole


class TokenRefresh(BaseModel):
    """Token 刷新请求"""

    refresh_token: str = Field(..., description="刷新 Token")


class TokenResponse(BaseModel):
    """Token 响应"""

    access_token: str
    refresh_token: str
    expires_in: int