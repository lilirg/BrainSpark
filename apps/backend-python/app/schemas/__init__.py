"""Pydantic 数据校验模型模块"""

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserLogin,
    UserLoginResponse,
    TokenRefresh,
    TokenResponse,
)
from app.schemas.class_ import (
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    ClassMemberResponse,
    AddMemberRequest,
)
from app.schemas.assessment import (
    AssessmentTypeResponse,
    AssessmentTaskCreate,
    AssessmentTaskResponse,
    AssessmentTaskUpdate,
    AssessmentResultResponse,
)

__all__ = [
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserLogin",
    "UserLoginResponse",
    "TokenRefresh",
    "TokenResponse",
    "ClassCreate",
    "ClassResponse",
    "ClassUpdate",
    "ClassMemberResponse",
    "AddMemberRequest",
    "AssessmentTypeResponse",
    "AssessmentTaskCreate",
    "AssessmentTaskResponse",
    "AssessmentTaskUpdate",
    "AssessmentResultResponse",
]