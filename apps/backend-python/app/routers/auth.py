"""认证路由 - 登录/刷新/登出"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success
from app.schemas.user import (
    TokenRefresh,
    UserLogin,
    UserLoginResponse,
)
from app.services.auth_service import AuthService, add_to_blacklist

router = APIRouter()


@router.post("/login", response_model=dict)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    service = AuthService(db)
    access_token, refresh_token, role = await service.authenticate(
        data.username, data.password
    )
    return success(
        data=UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=7200,
            role=role,
        ).model_dump()
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """刷新访问令牌"""
    service = AuthService(db)
    access_token, refresh_token = await service.refresh_token(
        data.refresh_token
    )
    return success(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 7200,
        }
    )


@router.post("/logout", response_model=dict)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """用户登出（将当前令牌加入黑名单）"""
    from app.core.logging import logger
    token = credentials.credentials
    add_to_blacklist(token)
    logger.info("用户登出成功，令牌已加入黑名单")
    return success(message="登出成功")