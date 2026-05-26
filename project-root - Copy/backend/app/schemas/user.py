from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    labeller_id: Optional[str] = None
    role_id: UUID
    shift_id: Optional[UUID] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    labeller_id: Optional[str] = None
    role_id: Optional[UUID] = None
    shift_id: Optional[UUID] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    name: str
    labeller_id: Optional[str]
    role: str  # role name
    shift_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True