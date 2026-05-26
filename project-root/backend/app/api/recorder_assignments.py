from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.database import get_db
from app.core.deps import get_current_active_user
from app.core.permissions import require_permission, _user_permission_codes  # type: ignore
from app.models.user import User
from app.schemas.recorder_assignment import (
    RecorderAssignmentCreate,
    RecorderAssignmentUpdate,
    RecorderAssignmentResponse,
    RecorderAssignmentSkip,
    RecorderAssignmentReassign,
)
from app.crud import recorder_assignment as crud

router = APIRouter()


@router.get("/", response_model=list[RecorderAssignmentResponse])
async def list_assignments(
    skip: int = 0,
    limit: int = 50,
    recorder_id: Optional[int] = None,
    task_id: Optional[int] = None,
    status: Optional[str] = None,
    shift_id: Optional[int] = None,
    assigned_date: Optional[date] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("assignments.list")),
):
    return await crud.list_assignments(
        db,
        skip=skip,
        limit=limit,
        recorder_id=recorder_id,
        task_id=task_id,
        status=status,
        shift_id=shift_id,
        assigned_date=assigned_date,
        is_active=is_active,
    )


@router.get("/mine", response_model=list[RecorderAssignmentResponse])
async def list_my_assignments(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    assigned_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await crud.list_assignments(
        db,
        skip=skip,
        limit=limit,
        recorder_id=current_user.user_id,
        status=status,
        assigned_date=assigned_date,
        is_active=True,
    )


@router.get("/{assignment_id}", response_model=RecorderAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = await crud.get_by_id(db, assignment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    # Owner can always see; otherwise needs assignments.get
    if row.recorder_id != current_user.user_id:
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "assignments.get" not in codes:
                raise HTTPException(status_code=403, detail="missing_permission:assignments.get")
    return row


@router.post("/", response_model=RecorderAssignmentResponse, status_code=201)
async def create_assignment(
    payload: RecorderAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("assignments.create")),
):
    return await crud.create(db, payload, actor_id=current_user.user_id)


@router.patch("/{assignment_id}", response_model=RecorderAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    payload: RecorderAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = await crud.get_by_id(db, assignment_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    # Recorder can move their own assignment through workflow transitions.
    if existing.recorder_id != current_user.user_id:
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "assignments.update" not in codes:
                raise HTTPException(
                    status_code=403, detail="missing_permission:assignments.update"
                )
    return await crud.update_assignment(db, assignment_id, payload, actor_id=current_user.user_id)


@router.post("/{assignment_id}/skip", response_model=RecorderAssignmentResponse)
async def skip_assignment(
    assignment_id: int,
    payload: RecorderAssignmentSkip,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = await crud.get_by_id(db, assignment_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    if existing.recorder_id != current_user.user_id:
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "assignments.skip" not in codes:
                raise HTTPException(
                    status_code=403, detail="missing_permission:assignments.skip"
                )
    return await crud.skip(db, assignment_id, payload.reason, actor_id=current_user.user_id)


@router.post("/{assignment_id}/reassign", response_model=RecorderAssignmentResponse, status_code=201)
async def reassign_assignment(
    assignment_id: int,
    payload: RecorderAssignmentReassign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("assignments.reassign")),
):
    new_row = await crud.reassign(
        db,
        assignment_id,
        new_recorder_id=payload.new_recorder_id,
        shift_id=payload.shift_id,
        actor_id=current_user.user_id,
    )
    if new_row is None:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    return new_row
