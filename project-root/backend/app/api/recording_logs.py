from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.core.deps import get_current_active_user
from app.core.permissions import require_permission, _user_permission_codes  # type: ignore
from app.models.user import User
from app.schemas.recording_log import (
    RecordingLogCreate,
    RecordingLogUpdate,
    RecordingLogResponse,
)
from app.crud import recording_log as crud
from app.crud import recorder_assignment as assignment_crud

router = APIRouter()


@router.get("/", response_model=list[RecordingLogResponse])
async def list_logs(
    skip: int = 0,
    limit: int = 50,
    recorder_id: Optional[int] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("recordings.list")),
):
    return await crud.list_logs(
        db, skip=skip, limit=limit, recorder_id=recorder_id, status=status, is_active=is_active
    )


@router.get("/mine", response_model=list[RecordingLogResponse])
async def list_my_logs(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await crud.list_logs(
        db, skip=skip, limit=limit, recorder_id=current_user.user_id, status=status, is_active=True
    )


@router.get("/{recording_log_id}", response_model=RecordingLogResponse)
async def get_log(
    recording_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = await crud.get_by_id(db, recording_log_id)
    if row is None:
        raise HTTPException(status_code=404, detail="recording_not_found")
    if row.recorder_id != current_user.user_id:
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "recordings.get" not in codes:
                raise HTTPException(
                    status_code=403, detail="missing_permission:recordings.get"
                )
    return row


@router.post("/", response_model=RecordingLogResponse, status_code=201)
async def create_log(
    payload: RecordingLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    assignment = await assignment_crud.get_by_id(db, payload.assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    # Only the assigned recorder can submit a recording for it (super_admin
    # bypass remains via permission code).
    if assignment.recorder_id != current_user.user_id:
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "recordings.create_any" not in codes:
                raise HTTPException(
                    status_code=403, detail="missing_permission:recordings.create_any"
                )
    if await crud.get_by_assignment(db, payload.assignment_id):
        raise HTTPException(status_code=409, detail="recording_already_exists")
    return await crud.create(
        db, payload, recorder_id=assignment.recorder_id, actor_id=current_user.user_id
    )


@router.patch("/{recording_log_id}", response_model=RecordingLogResponse)
async def update_log(
    recording_log_id: int,
    payload: RecordingLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = await crud.get_by_id(db, recording_log_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="recording_not_found")
    # Recorder can edit their own pending recording; status changes (approve/
    # reject/rework) require the QA permission.
    is_status_change = payload.status is not None and payload.status != existing.status
    if is_status_change:
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "recordings.review" not in codes:
                raise HTTPException(
                    status_code=403, detail="missing_permission:recordings.review"
                )
    elif existing.recorder_id != current_user.user_id:
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "recordings.update" not in codes:
                raise HTTPException(
                    status_code=403, detail="missing_permission:recordings.update"
                )
    return await crud.update_log(db, recording_log_id, payload, actor_id=current_user.user_id)
