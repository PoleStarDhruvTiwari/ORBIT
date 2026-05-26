from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=1)


class TaskCategoryCreate(TaskCategoryBase):
    pass


class TaskCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None


class TaskCategoryResponse(TaskCategoryBase):
    task_category_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
