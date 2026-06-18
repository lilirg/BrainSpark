"""认证服务 - JWT 登录/刷新/登出"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.models.user import User, UserRole
from app.services.user_service import UserService

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对密码进行哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, role: UserRole) -> str:
    """创建访问令牌"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "exp": expire,
        "type": "access",
        "aud": "brainspark:access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """创建刷新令牌"""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "aud": "brainspark:refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_aud: str = "brainspark:access") -> dict:
    """解码并验证 JWT 令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=expected_aud,
        )
        return payload
    except JWTError:
        raise UnauthorizedError("无效的访问令牌")


class TokenBlacklist:
    """带 TTL 过期机制的令牌黑名单

    使用 OrderedDict 实现，自动清理过期令牌。
    TTL 默认与 access_token 过期时间一致（2小时），
    确保黑名单不会无限增长。

    生产环境建议替换为 Redis 实现。
    """

    def __init__(self, ttl_seconds: int | None = None) -> None:
        self._cache: OrderedDict[str, float] = OrderedDict()
        self._lock = threading.Lock()
        # 默认 TTL 与 access_token 过期时间一致
        self._ttl = ttl_seconds or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    def add(self, token: str) -> None:
        """将令牌加入黑名单"""
        with self._lock:
            self._evict_expired()
            self._cache[token] = time.time()

    def contains(self, token: str) -> bool:
        """检查令牌是否在黑名单中"""
        with self._lock:
            self._evict_expired()
            return token in self._cache

    def _evict_expired(self) -> None:
        """清理已过期的令牌"""
        now = time.time()
        while self._cache:
            # peek 最早插入的条目
            _, added_at = next(iter(self._cache.items()))
            if now - added_at < self._ttl:
                break
            self._cache.popitem(last=False)

    @property
    def size(self) -> int:
        """当前黑名单大小"""
        with self._lock:
            return len(self._cache)


# 全局令牌黑名单实例（临时方案，Redis 就绪后替换）
token_blacklist = TokenBlacklist()


def add_to_blacklist(token: str) -> None:
    """将令牌加入黑名单"""
    token_blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    """检查令牌是否在黑名单中"""
    return token_blacklist.contains(token)


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_service = UserService(db)

    async def authenticate(self, username: str, password: str) -> tuple[str, str, UserRole]:
        """用户认证，返回 (access_token, refresh_token, role)"""
        user = await self.user_service.get_user_by_username(username)
        if not user:
            raise UnauthorizedError("用户名或密码错误")

        if not verify_password(password, user.password):
            raise UnauthorizedError("用户名或密码错误")

        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        return access_token, refresh_token, user.role

    async def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        """刷新访问令牌"""
        payload = decode_token(refresh_token, expected_aud="brainspark:refresh")

        if payload.get("type") != "refresh":
            raise UnauthorizedError("无效的刷新令牌")

        user_id = int(payload["sub"])
        user = await self.user_service.get_user_by_id(user_id)

        new_access_token = create_access_token(user.id, user.role)
        new_refresh_token = create_refresh_token(user.id)

        return new_access_token, new_refresh_token

    @staticmethod
    def get_current_user_id(token: str) -> int:
        """从访问令牌中获取当前用户 ID"""
        payload = decode_token(token, expected_aud="brainspark:access")
        if payload.get("type") != "access":
            raise UnauthorizedError("无效的访问令牌")
        return int(payload["sub"])


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """从请求头中提取并验证 JWT 令牌，返回当前用户 ID"""
    token = credentials.credentials
    if is_token_blacklisted(token):
        raise UnauthorizedError("令牌已失效，请重新登录")
    return AuthService.get_current_user_id(token)