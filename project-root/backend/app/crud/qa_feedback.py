from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional

from app.models.qa_feedback import QAFeedback
from app.schemas.qa_feedback import QAFeedbackCreate, QAFeedbackUpdate


async def get_by_id(db: AsyncSession, qa_feedback_id: int) -> Optional[QAFeedback]:
    res = await db.execute(select(QAFeedback).where(QAFeedback.qa_feedback_id == qa_feedback_id))
    return res.scalar_one_or_none()


async def list_feedback(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    recording_log_id: Optional[int] = None,
    qa_user_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> list[QAFeedback]:
    q = select(QAFeedback)
    if recording_log_id is not None:
        q = q.where(QAFeedback.recording_log_id == recording_log_id)
    if qa_user_id is not None:
        q = q.where(QAFeedback.qa_user_id == qa_user_id)
    if is_active is not None:
        q = q.where(QAFeedback.is_active == is_active)
    q = q.order_by(QAFeedback.created_at.desc()).offset(skip).limit(limit)
    return list((await db.execute(q)).scalars().all())


async def create(
    db: AsyncSession, payload: QAFeedbackCreate, qa_user_id: int
) -> QAFeedback:
    row = QAFeedback(
        recording_log_id=payload.recording_log_id,
        qa_user_id=qa_user_id,
        pass_rate=payload.pass_rate,
        feedback_text=payload.feedback_text,
        is_rework_required=payload.is_rework_required,
        feedback_category=payload.feedback_category,
        created_by=qa_user_id,
        updated_by=qa_user_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_feedback(
    db: AsyncSession, qa_feedback_id: int, payload: QAFeedbackUpdate, actor_id: int
) -> Optional[QAFeedback]:
    values = payload.dict(exclude_unset=True)
    if values:
        values["updated_by"] = actor_id
        await db.execute(
            update(QAFeedback).where(QAFeedback.qa_feedback_id == qa_feedback_id).values(**values)
        )
        await db.commit()
    return await get_by_id(db, qa_feedback_id)
