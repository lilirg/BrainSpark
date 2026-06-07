"""业务服务模块"""

from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.class_service import ClassService
from app.services.student_service import StudentService
from app.services.assessment_service import AssessmentService

__all__ = [
    "UserService",
    "AuthService",
    "ClassService",
    "StudentService",
    "AssessmentService",
]