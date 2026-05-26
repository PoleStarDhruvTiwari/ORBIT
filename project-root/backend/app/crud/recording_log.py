from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional

from app.models.recording_log import RecordingLog
from app.schemas.recording_log import RecordingLogCreate, RecordingLogUpdate


async def get_by_id(db: AsyncSession, recording_log_id: int) -> Optional[RecordingLog]:
    res = await db.execute(
        select(RecordingLog).where(RecordingLog.recording_log_id == recording_log_id)
    )
    return res.scalar_one_or_none()


async def get_by_assignment(db: AsyncSession, assignment_id: int) -> Optional[RecordingLog]:
    res = await db.execute(
        select(RecordingLog).where(RecordingLog.assignment_id == assignment_id)
    )
    return res.scalar_one_or_none()


async def list_logs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    recorder_id: Optional[int] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> list[RecordingLog]:
    q = select(RecordingLog)
    if recorder_id is not None:
        q = q.where(RecordingLog.recorder_id == recorder_id)
    if status is not None:
        q = q.where(RecordingLog.status == status)
    if is_active is not None:
        q = q.where(RecordingLog.is_active == is_active)
    q = q.order_by(RecordingLog.recorded_at.desc()).offset(skip).limit(limit)
    return list((await db.execute(q)).scalars().all())


async def create(
    db: AsyncSession, payload: RecordingLogCreate, recorder_id: int, actor_id: int
) -> RecordingLog:
    row = RecordingLog(
        assignment_id=payload.assignment_id,
        actual_time_minutes=payload.actual_time_minutes,
        comment=payload.comment,
        recorder_id=recorder_id,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_log(
    db: AsyncSession, recording_log_id: int, payload: RecordingLogUpdate, actor_id: int
) -> Optional[RecordingLog]:
    values = payload.dict(exclude_unset=True)
    if values:
        values["updated_by"] = actor_id
        await db.execute(
            update(RecordingLog)
            .where(RecordingLog.recording_log_id == recording_log_id)
            .values(**values)
        )
        await db.commit()
    return await get_by_id(db, recording_log_id)
