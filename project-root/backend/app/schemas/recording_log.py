from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


RecordingStatus = Literal["pending_review", "approved", "rejected", "rework_needed"]


class RecordingLogBase(BaseModel):
    assignment_id: int = Field(..., ge=1)
    actual_time_minutes: int = Field(..., ge=0, le=60)
    comment: Optional[str] = Field(None, max_length=4000)


class RecordingLogCreate(RecordingLogBase):
    pass


class RecordingLogUpdate(BaseModel):
    status: Optional[RecordingStatus] = None
    actual_time_minutes: Optional[int] = Field(None, ge=0, le=60)
    comment: Optional[str] = Field(None, max_length=4000)
    is_active: Optional[bool] = None


class RecordingLogResponse(BaseModel):
    recording_log_id: int
    assignment_id: int
    recorder_id: int
    status: RecordingStatus
    actual_time_minutes: int
    comment: Optional[str]
    recorded_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
