"""测评管理服务"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.assessment import AssessmentResult, AssessmentTask, AssessmentType
from app.schemas.assessment import AssessmentTaskCreate, AssessmentTaskUpdate


class AssessmentService:
    """测评管理服务"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # === 测评类型 ===
    async def list_types(self) -> list[AssessmentType]:
        """获取所有测评类型"""
        result = await self.db.execute(
            select(AssessmentType).where(AssessmentType.is_published == True)
        )
        return list(result.scalars().all())

    # === 测评任务 ===
    async def list_tasks(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[AssessmentTask], int]:
        """获取测评任务列表（分页）"""
        count_result = await self.db.execute(
            select(func.count()).select_from(AssessmentTask).where(AssessmentTask.is_active == True)
        )
        total = count_result.scalar()

        offset = (page - 1) * size
        result = await self.db.execute(
            select(AssessmentTask)
            .where(AssessmentTask.is_active == True)
            .offset(offset)
            .limit(size)
        )
        tasks = list(result.scalars().all())
        return tasks, total

    async def get_task_by_id(self, task_id: int) -> AssessmentTask:
        """根据 ID 获取测评任务"""
        result = await self.db.execute(
            select(AssessmentTask).where(AssessmentTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError(f"测评任务不存在: id={task_id}")
        return task

    async def create_task(self, data: AssessmentTaskCreate) -> AssessmentTask:
        """创建测评任务"""
        task = AssessmentTask(
            title=data.title,
            type_code=data.type_code,
            class_id=data.class_id,
            difficulty=data.difficulty,
            duration_min=data.duration_min,
            start_at=data.start_at,
            end_at=data.end_at,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update_task(
        self, task_id: int, data: AssessmentTaskUpdate
    ) -> AssessmentTask:
        """更新测评任务"""
        task = await self.get_task_by_id(task_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task_id: int) -> None:
        """删除测评任务（软删除）"""
        task = await self.get_task_by_id(task_id)
        task.is_active = False
        await self.db.flush()

    async def get_today_tasks(self, user_id: int) -> list[AssessmentTask]:
        """获取今日待测任务"""
        today = date.today()
        day_start = datetime.combine(today, datetime.min.time())
        day_end = datetime.combine(today, datetime.max.time())

        result = await self.db.execute(
            select(AssessmentTask).where(
                AssessmentTask.is_active == True,
                # 任务在今天范围内（时间段有重叠）：
                # start_at 为 NULL 或 start_at <= day_end
                (AssessmentTask.start_at == None) | (AssessmentTask.start_at <= day_end),
                # end_at 为 NULL 或 end_at >= day_start
                (AssessmentTask.end_at == None) | (AssessmentTask.end_at >= day_start),
            )
        )
        return list(result.scalars().all())

    # === 测评结果 ===
    async def list_results(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[AssessmentResult], int]:
        """获取测评结果列表（分页）"""
        count_result = await self.db.execute(
            select(func.count()).select_from(AssessmentResult)
        )
        total = count_result.scalar()

        offset = (page - 1) * size
        result = await self.db.execute(
            select(AssessmentResult).offset(offset).limit(size)
        )
        results = list(result.scalars().all())
        return results, total

    async def get_result_by_id(self, result_id: int) -> AssessmentResult:
        """根据 ID 获取测评结果"""
        result = await self.db.execute(
            select(AssessmentResult).where(AssessmentResult.id == result_id)
        )
        assessment_result = result.scalar_one_or_none()
        if not assessment_result:
            raise NotFoundError(f"测评结果不存在: id={result_id}")
        return assessment_result