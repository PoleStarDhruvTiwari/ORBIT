from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


FeedbackCategory = Literal["accuracy", "completeness", "speed", "guidelines"]


class QAFeedbackBase(BaseModel):
    recording_log_id: int = Field(..., ge=1)
    pass_rate: int = Field(..., ge=0, le=100)
    feedback_text: str = Field(..., min_length=3, max_length=4000)
    is_rework_required: bool = False
    feedback_category: FeedbackCategory


class QAFeedbackCreate(QAFeedbackBase):
    pass


class QAFeedbackUpdate(BaseModel):
    pass_rate: Optional[int] = Field(None, ge=0, le=100)
    feedback_text: Optional[str] = Field(None, min_length=3, max_length=4000)
    is_rework_required: Optional[bool] = None
    feedback_category: Optional[FeedbackCategory] = None
    is_active: Optional[bool] = None


class QAFeedbackResponse(QAFeedbackBase):
    qa_feedback_id: int
    qa_user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
