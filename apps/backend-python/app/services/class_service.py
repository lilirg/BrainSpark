"""班级管理服务"""

from __future__ import annotations

from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.class_ import Class, ClassMember
from app.schemas.class_ import ClassCreate, ClassUpdate, AddMemberRequest


class ClassService:
    """班级管理服务"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_classes(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[Class], int]:
        """获取班级列表（分页）"""
        # 查询总数
        count_result = await self.db.execute(
            select(func.count()).select_from(Class).where(Class.is_active == True)
        )
        total = count_result.scalar()

        # 分页查询
        offset = (page - 1) * size
        result = await self.db.execute(
            select(Class)
            .where(Class.is_active == True)
            .offset(offset)
            .limit(size)
        )
        classes = list(result.scalars().all())
        return classes, total

    async def get_class_by_id(self, class_id: int) -> Class:
        """根据 ID 获取班级"""
        result = await self.db.execute(
            select(Class).where(Class.id == class_id)
        )
        class_ = result.scalar_one_or_none()
        if not class_:
            raise NotFoundError(f"班级不存在: id={class_id}")
        return class_

    async def create_class(self, data: ClassCreate) -> Class:
        """创建班级"""
        class_ = Class(
            name=data.name,
            grade=data.grade,
            description=data.description,
            teacher_id=data.teacher_id,
            max_students=data.max_students,
        )
        self.db.add(class_)
        await self.db.flush()
        await self.db.refresh(class_)
        return class_

    async def update_class(self, class_id: int, data: ClassUpdate) -> Class:
        """更新班级信息"""
        class_ = await self.get_class_by_id(class_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(class_, field, value)
        await self.db.flush()
        await self.db.refresh(class_)
        return class_

    async def delete_class(self, class_id: int) -> None:
        """删除班级（软删除）"""
        class_ = await self.get_class_by_id(class_id)
        class_.is_active = False
        await self.db.flush()

    async def list_members(self, class_id: int) -> list[ClassMember]:
        """获取班级成员列表"""
        # 验证班级存在
        await self.get_class_by_id(class_id)

        result = await self.db.execute(
            select(ClassMember).where(ClassMember.class_id == class_id)
        )
        return list(result.scalars().all())

    async def add_member(self, class_id: int, data: AddMemberRequest) -> ClassMember:
        """添加班级成员"""
        # 验证班级存在
        await self.get_class_by_id(class_id)

        # 检查是否已是成员
        result = await self.db.execute(
            select(ClassMember).where(
                ClassMember.class_id == class_id,
                ClassMember.user_id == data.user_id,
            )
        )
        if result.scalar_one_or_none():
            raise ConflictError("该用户已是班级成员")

        member = ClassMember(
            class_id=class_id,
            user_id=data.user_id,
            role=data.role,
        )
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(self, class_id: int, user_id: int) -> None:
        """移除班级成员"""
        result = await self.db.execute(
            select(ClassMember).where(
                ClassMember.class_id == class_id,
                ClassMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise NotFoundError("该用户不是班级成员")
        await self.db.delete(member)
        await self.db.flush()