from pydantic import BaseModel, Field, field_validator
from datetime import time, datetime
from typing import Optional, Literal


ShiftName = Literal["morning", "evening", "night"]


class ShiftBase(BaseModel):
    name: ShiftName
    start_time: time
    end_time: time
    description: str = Field(..., min_length=1, max_length=500)

    @field_validator("end_time")
    @classmethod
    def _end_not_equal_start(cls, v, info):
        start = info.data.get("start_time")
        if start is not None and v == start:
            raise ValueError("end_time must differ from start_time")
        return v


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    is_active: Optional[bool] = None


class ShiftResponse(ShiftBase):
    shift_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
