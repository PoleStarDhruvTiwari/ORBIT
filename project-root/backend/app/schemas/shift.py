from pydantic import BaseModel
from uuid import UUID
from datetime import time, datetime
from typing import Optional

class ShiftBase(BaseModel):
    name: str  # Morning, Evening, Night
    start_time: time
    end_time: time
    description: Optional[str] = None

class ShiftCreate(ShiftBase):
    pass

class ShiftUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ShiftResponse(ShiftBase):
    shift_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True