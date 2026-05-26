from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.qa_feedback import (
    QAFeedbackCreate,
    QAFeedbackUpdate,
    QAFeedbackResponse,
)
from app.crud import qa_feedback as crud
from app.crud import recording_log as recording_crud

router = APIRouter()


@router.get("/", response_model=list[QAFeedbackResponse])
async def list_feedback(
    skip: int = 0,
    limit: int = 50,
    recording_log_id: Optional[int] = None,
    qa_user_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("qa_feedback.list")),
):
    return await crud.list_feedback(
        db,
        skip=skip,
        limit=limit,
        recording_log_id=recording_log_id,
        qa_user_id=qa_user_id,
        is_active=is_active,
    )


@router.post("/", response_model=QAFeedbackResponse, status_code=201)
async def create_feedback(
    payload: QAFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("qa_feedback.create")),
):
    if not await recording_crud.get_by_id(db, payload.recording_log_id):
        raise HTTPException(status_code=404, detail="recording_not_found")
    return await crud.create(db, payload, qa_user_id=current_user.user_id)


@router.patch("/{qa_feedback_id}", response_model=QAFeedbackResponse)
async def update_feedback(
    qa_feedback_id: int,
    payload: QAFeedbackUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("qa_feedback.update")),
):
    row = await crud.update_feedback(db, qa_feedback_id, payload, actor_id=current_user.user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="qa_feedback_not_found")
    return row
