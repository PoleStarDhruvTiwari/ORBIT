from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Literal


AssignmentStatus = Literal[
    "assigned",
    "in_progress",
    "submitted",
    "qa_review_pending",
    "completed",
    "rejected",
    "skipped",
    "reassigned",
]


class RecorderAssignmentBase(BaseModel):
    task_id: int = Field(..., ge=1)
    recorder_id: int = Field(..., ge=1)
    shift_id: int = Field(..., ge=1)
    assigned_date: Optional[date] = None


class RecorderAssignmentCreate(RecorderAssignmentBase):
    pass


class RecorderAssignmentUpdate(BaseModel):
    status: Optional[AssignmentStatus] = None
    completed_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class RecorderAssignmentSkip(BaseModel):
    reason: str = Field(..., min_length=3, max_length=2000)


class RecorderAssignmentReassign(BaseModel):
    new_recorder_id: int = Field(..., ge=1)
    shift_id: Optional[int] = Field(None, ge=1)


class RecorderAssignmentResponse(BaseModel):
    recorder_assignment_id: int
    task_id: int
    recorder_id: int
    assigned_by: int
    assigned_date: date
    shift_id: int
    status: AssignmentStatus
    completed_at: Optional[datetime]
    skipped_reason: Optional[str]
    reassigned_from_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
