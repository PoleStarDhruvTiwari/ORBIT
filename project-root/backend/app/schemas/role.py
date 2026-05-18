from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    can_assign_tasks: bool = False
    can_create_tasks: bool = False
    can_review_quality: bool = False
    can_manage_users: bool = False
    can_view_reports: bool = False

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    can_assign_tasks: Optional[bool] = None
    can_create_tasks: Optional[bool] = None
    can_review_quality: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_view_reports: Optional[bool] = None

class RoleResponse(RoleBase):
    role_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True