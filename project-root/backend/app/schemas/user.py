from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# Labeller IDs are uppercase alphanumeric with optional dashes/underscores.
_LABELLER_PATTERN = r"^[A-Za-z0-9_-]{2,50}$"


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    labeller_id: str = Field(..., pattern=_LABELLER_PATTERN)
    role_id: int = Field(..., ge=1)
    shift_id: int = Field(..., ge=1)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    labeller_id: Optional[str] = Field(None, pattern=_LABELLER_PATTERN)
    role_id: Optional[int] = Field(None, ge=1)
    shift_id: Optional[int] = Field(None, ge=1)
    is_approved: Optional[bool] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: str
    labeller_id: str
    role: str  # role name, joined in API
    shift_id: int
    is_approved: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
