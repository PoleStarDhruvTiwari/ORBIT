from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional

from app.models.task_category import TaskCategory
from app.schemas.task_category import TaskCategoryCreate, TaskCategoryUpdate


async def get_by_id(db: AsyncSession, task_category_id: int) -> Optional[TaskCategory]:
    res = await db.execute(
        select(TaskCategory).where(TaskCategory.task_category_id == task_category_id)
    )
    return res.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Optional[TaskCategory]:
    res = await db.execute(select(TaskCategory).where(TaskCategory.name == name))
    return res.scalar_one_or_none()


async def list_categories(
    db: AsyncSession, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> list[TaskCategory]:
    q = select(TaskCategory)
    if is_active is not None:
        q = q.where(TaskCategory.is_active == is_active)
    q = q.order_by(TaskCategory.name).offset(skip).limit(limit)
    return list((await db.execute(q)).scalars().all())


async def create(
    db: AsyncSession, payload: TaskCategoryCreate, actor_id: int
) -> TaskCategory:
    row = TaskCategory(
        name=payload.name,
        description=payload.description,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_category(
    db: AsyncSession, task_category_id: int, payload: TaskCategoryUpdate, actor_id: int
) -> Optional[TaskCategory]:
    values = payload.dict(exclude_unset=True)
    if values:
        values["updated_by"] = actor_id
        await db.execute(
            update(TaskCategory)
            .where(TaskCategory.task_category_id == task_category_id)
            .values(**values)
        )
        await db.commit()
    return await get_by_id(db, task_category_id)
