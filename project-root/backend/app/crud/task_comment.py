from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task_comment import TaskComment
from app.schemas.task_comment import TaskCommentCreate


async def list_for_task(
    db: AsyncSession, task_id: int, skip: int = 0, limit: int = 100
) -> list[TaskComment]:
    q = (
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    return list((await db.execute(q)).scalars().all())


async def create(
    db: AsyncSession, payload: TaskCommentCreate, author_id: int
) -> TaskComment:
    row = TaskComment(
        task_id=payload.task_id,
        author_id=author_id,
        kind=payload.kind,
        body=payload.body,
        status_from=payload.status_from,
        status_to=payload.status_to,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
