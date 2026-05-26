from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
from typing import Optional

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def get_by_id(db: AsyncSession, task_id: int) -> Optional[Task]:
    res = await db.execute(select(Task).where(Task.task_id == task_id))
    return res.scalar_one_or_none()


async def get_by_key(db: AsyncSession, task_key: str) -> Optional[Task]:
    res = await db.execute(select(Task).where(Task.task_key == task_key))
    return res.scalar_one_or_none()


async def list_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    environment: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> list[Task]:
    q = select(Task)
    if status is not None:
        q = q.where(Task.status == status)
    if task_type is not None:
        q = q.where(Task.task_type == task_type)
    if category_id is not None:
        q = q.where(Task.category_id == category_id)
    if priority is not None:
        q = q.where(Task.priority == priority)
    if environment is not None:
        q = q.where(Task.environment == environment)
    if is_active is not None:
        q = q.where(Task.is_active == is_active)
    if search:
        like = f"%{search}%"
        q = q.where(or_(Task.title.ilike(like), Task.task_key.ilike(like)))
    q = q.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    return list((await db.execute(q)).scalars().all())


async def create(db: AsyncSession, payload: TaskCreate, actor_id: int) -> Task:
    row = Task(
        **payload.dict(),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_task(
    db: AsyncSession, task_id: int, payload: TaskUpdate, actor_id: int
) -> Optional[Task]:
    values = payload.dict(exclude_unset=True)
    if values:
        values["updated_by"] = actor_id
        await db.execute(update(Task).where(Task.task_id == task_id).values(**values))
        await db.commit()
    return await get_by_id(db, task_id)


async def set_status(
    db: AsyncSession, task_id: int, new_status: str, actor_id: int
) -> Optional[Task]:
    await db.execute(
        update(Task)
        .where(Task.task_id == task_id)
        .values(status=new_status, updated_by=actor_id)
    )
    await db.commit()
    return await get_by_id(db, task_id)


async def soft_delete(db: AsyncSession, task_id: int, actor_id: int) -> None:
    await db.execute(
        update(Task).where(Task.task_id == task_id).values(is_active=False, updated_by=actor_id)
    )
    await db.commit()


async def replicate(
    db: AsyncSession, source_task_id: int, actor_id: int, new_task_key: str
) -> Optional[Task]:
    src = await get_by_id(db, source_task_id)
    if src is None:
        return None
    clone = Task(
        task_key=new_task_key,
        category_id=src.category_id,
        environment=src.environment,
        priority=src.priority,
        task_type=src.task_type,
        title=src.title,
        description=src.description,
        task_script=src.task_script,
        estimated_time_minutes=src.estimated_time_minutes,
        source_sheet_name=src.source_sheet_name,
        source_row_id=src.source_row_id,
        replicated_from=src.task_id,
        status="draft",
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return clone
