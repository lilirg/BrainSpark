"""
AI 服务 API 路由
"""
from fastapi import APIRouter
from .assessments import router as assessments_router
from .reports import router as reports_router
from .knowledge import router as knowledge_router

router = APIRouter(prefix="/ai/v1")
router.include_router(assessments_router)
router.include_router(reports_router)
router.include_router(knowledge_router)