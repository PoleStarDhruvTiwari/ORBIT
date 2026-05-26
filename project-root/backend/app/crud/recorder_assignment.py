from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone, date
from typing import Optional

from app.models.recorder_assignment import RecorderAssignment
from app.schemas.recorder_assignment import (
    RecorderAssignmentCreate,
    RecorderAssignmentUpdate,
)


async def get_by_id(db: AsyncSession, assignment_id: int) -> Optional[RecorderAssignment]:
    res = await db.execute(
        select(RecorderAssignment).where(
            RecorderAssignment.recorder_assignment_id == assignment_id
        )
    )
    return res.scalar_one_or_none()


async def list_assignments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    recorder_id: Optional[int] = None,
    task_id: Optional[int] = None,
    status: Optional[str] = None,
    shift_id: Optional[int] = None,
    assigned_date: Optional[date] = None,
    is_active: Optional[bool] = None,
) -> list[RecorderAssignment]:
    q = select(RecorderAssignment)
    if recorder_id is not None:
        q = q.where(RecorderAssignment.recorder_id == recorder_id)
    if task_id is not None:
        q = q.where(RecorderAssignment.task_id == task_id)
    if status is not None:
        q = q.where(RecorderAssignment.status == status)
    if shift_id is not None:
        q = q.where(RecorderAssignment.shift_id == shift_id)
    if assigned_date is not None:
        q = q.where(RecorderAssignment.assigned_date == assigned_date)
    if is_active is not None:
        q = q.where(RecorderAssignment.is_active == is_active)
    q = q.order_by(RecorderAssignment.created_at.desc()).offset(skip).limit(limit)
    return list((await db.execute(q)).scalars().all())


async def create(
    db: AsyncSession, payload: RecorderAssignmentCreate, actor_id: int
) -> RecorderAssignment:
    data = payload.dict(exclude_unset=True)
    row = RecorderAssignment(
        **data,
        assigned_by=actor_id,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_assignment(
    db: AsyncSession, assignment_id: int, payload: RecorderAssignmentUpdate, actor_id: int
) -> Optional[RecorderAssignment]:
    values = payload.dict(exclude_unset=True)
    if values.get("status") == "completed" and "completed_at" not in values:
        values["completed_at"] = datetime.now(timezone.utc)
    if values:
        values["updated_by"] = actor_id
        await db.execute(
            update(RecorderAssignment)
            .where(RecorderAssignment.recorder_assignment_id == assignment_id)
            .values(**values)
        )
        await db.commit()
    return await get_by_id(db, assignment_id)


async def skip(
    db: AsyncSession, assignment_id: int, reason: str, actor_id: int
) -> Optional[RecorderAssignment]:
    await db.execute(
        update(RecorderAssignment)
        .where(RecorderAssignment.recorder_assignment_id == assignment_id)
        .values(status="skipped", skipped_reason=reason, updated_by=actor_id)
    )
    await db.commit()
    return await get_by_id(db, assignment_id)


async def reassign(
    db: AsyncSession,
    assignment_id: int,
    new_recorder_id: int,
    shift_id: Optional[int],
    actor_id: int,
) -> Optional[RecorderAssignment]:
    src = await get_by_id(db, assignment_id)
    if src is None:
        return None
    await db.execute(
        update(RecorderAssignment)
        .where(RecorderAssignment.recorder_assignment_id == assignment_id)
        .values(status="reassigned", updated_by=actor_id)
    )
    new_row = RecorderAssignment(
        task_id=src.task_id,
        recorder_id=new_recorder_id,
        assigned_by=actor_id,
        assigned_date=date.today(),
        shift_id=shift_id or src.shift_id,
        status="assigned",
        reassigned_from_id=src.recorder_assignment_id,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(new_row)
    await db.commit()
    await db.refresh(new_row)
    return new_row
