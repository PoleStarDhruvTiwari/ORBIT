from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.task_replication import (
    TaskReplicationCreate,
    TaskReplicationResponse,
)
from app.crud import task_replication as crud
from app.crud import recording_log as recording_crud

router = APIRouter()


@router.get("/", response_model=list[TaskReplicationResponse])
async def list_replications(
    skip: int = 0,
    limit: int = 50,
    original_task_id: Optional[int] = None,
    recording_log_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("task_replications.list")),
):
    return await crud.list_replications(
        db,
        skip=skip,
        limit=limit,
        original_task_id=original_task_id,
        recording_log_id=recording_log_id,
        is_active=is_active,
    )


@router.post("/", response_model=TaskReplicationResponse, status_code=201)
async def create_replication(
    payload: TaskReplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("task_replications.create")),
):
    log = await recording_crud.get_by_id(db, payload.recording_log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="recording_not_found")
    if log.status != "approved":
        raise HTTPException(status_code=400, detail="recording_not_approved")
    return await crud.create(db, payload, actor_id=current_user.user_id)
