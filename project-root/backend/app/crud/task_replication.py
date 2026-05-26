from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.task_replication import TaskReplication
from app.schemas.task_replication import TaskReplicationCreate


async def get_by_id(db: AsyncSession, task_replication_id: int) -> Optional[TaskReplication]:
    res = await db.execute(
        select(TaskReplication).where(
            TaskReplication.task_replication_id == task_replication_id
        )
    )
    return res.scalar_one_or_none()


async def list_replications(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    original_task_id: Optional[int] = None,
    recording_log_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> list[TaskReplication]:
    q = select(TaskReplication)
    if original_task_id is not None:
        q = q.where(TaskReplication.original_task_id == original_task_id)
    if recording_log_id is not None:
        q = q.where(TaskReplication.recording_log_id == recording_log_id)
    if is_active is not None:
        q = q.where(TaskReplication.is_active == is_active)
    q = q.order_by(TaskReplication.created_at.desc()).offset(skip).limit(limit)
    return list((await db.execute(q)).scalars().all())


async def create(
    db: AsyncSession, payload: TaskReplicationCreate, actor_id: int
) -> TaskReplication:
    row = TaskReplication(
        original_task_id=payload.original_task_id,
        recording_log_id=payload.recording_log_id,
        environment_type=payload.environment_type,
        environment_identifier=payload.environment_identifier,
        replicated_by=actor_id,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
