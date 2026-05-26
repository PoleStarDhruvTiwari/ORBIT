from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


TaskEnvironment = Literal["office/outdoor", "outdoor", "office"]


class TaskReplicationBase(BaseModel):
    original_task_id: int = Field(..., ge=1)
    recording_log_id: int = Field(..., ge=1)
    environment_type: TaskEnvironment
    environment_identifier: str = Field(..., min_length=1, max_length=255)


class TaskReplicationCreate(TaskReplicationBase):
    pass


class TaskReplicationResponse(TaskReplicationBase):
    task_replication_id: int
    replicated_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
