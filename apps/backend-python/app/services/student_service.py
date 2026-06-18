"""学生档案服务"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.models.student import StudentProfile
from app.schemas.student import StudentProfileUpdate, GrowthRecord


class StudentService:
    """学生档案服务"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_profile(self, user_id: int) -> StudentProfile:
        """获取学生档案"""
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError(f"学生档案不存在: user_id={user_id}")
        return profile

    async def create_or_update_profile(
        self, user_id: int, data: StudentProfileUpdate
    ) -> StudentProfile:
        """创建或更新学生档案"""
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if profile:
            # 更新现有档案
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(profile, field, value)
        else:
            # 创建新档案
            profile = StudentProfile(user_id=user_id, **data.model_dump(exclude_unset=True))
            self.db.add(profile)

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def get_growth_trend(self, user_id: int) -> list[GrowthRecord]:
        """获取学生成长趋势数据

        从 assessment_results 表中聚合历史测评数据，
        按日期分组返回各维度的雷达图数据。
        """
        from app.core.exceptions import ServiceUnavailableError
        raise ServiceUnavailableError("成长趋势功能开发中，待 assessment_results 表数据就绪后实现")