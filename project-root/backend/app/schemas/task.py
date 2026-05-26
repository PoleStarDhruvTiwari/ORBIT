from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


TaskStatus = Literal["draft", "approved", "rejected", "archived"]
TaskType = Literal["general", "niche"]
TaskPriority = Literal["P0", "P1", "P2", "P3"]
TaskEnvironment = Literal["office/outdoor", "outdoor", "office"]


_TASK_KEY_PATTERN = r"^[A-Za-z0-9_-]{2,50}$"


class TaskBase(BaseModel):
    task_key: str = Field(..., pattern=_TASK_KEY_PATTERN)
    category_id: int = Field(..., ge=1)
    environment: TaskEnvironment
    priority: TaskPriority = "P2"
    task_type: TaskType = "general"
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    task_script: Optional[str] = None
    estimated_time_minutes: int = Field(..., ge=2, le=15)
    source_sheet_name: Optional[str] = Field(None, max_length=255)
    source_row_id: Optional[str] = Field(None, max_length=100)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    category_id: Optional[int] = Field(None, ge=1)
    environment: Optional[TaskEnvironment] = None
    priority: Optional[TaskPriority] = None
    task_type: Optional[TaskType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    task_script: Optional[str] = None
    estimated_time_minutes: Optional[int] = Field(None, ge=2, le=15)
    status: Optional[TaskStatus] = None
    is_active: Optional[bool] = None


class TaskStatusChange(BaseModel):
    status: TaskStatus
    comment: Optional[str] = Field(None, max_length=4000)


class TaskResponse(TaskBase):
    task_id: int
    status: TaskStatus
    replicated_from: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
