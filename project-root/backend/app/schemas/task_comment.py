from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, Literal


TaskStatus = Literal["draft", "approved", "rejected", "archived"]
TaskCommentKind = Literal[
    "comment",
    "status_change",
    "skip_requested",
    "skip_approved",
    "skip_rejected",
    "submitted",
    "created",
    "assigned",
]


class TaskCommentCreate(BaseModel):
    task_id: int = Field(..., ge=1)
    kind: TaskCommentKind = "comment"
    body: Optional[str] = Field(None, max_length=4000)
    status_from: Optional[TaskStatus] = None
    status_to: Optional[TaskStatus] = None

    @model_validator(mode="after")
    def _kind_body_consistency(self):
        if self.kind == "comment" and not (self.body and self.body.strip()):
            raise ValueError("body is required for comment kind")
        return self


class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    author_id: int
    kind: TaskCommentKind
    body: Optional[str]
    status_from: Optional[TaskStatus]
    status_to: Optional[TaskStatus]
    created_at: datetime

    class Config:
        from_attributes = True
