from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class RoleBase(BaseModel):
    name: str  # role_name_enum
    description: str
    can_assign_tasks: bool = False
    can_create_tasks: bool = False
    can_review_quality: bool = False
    can_manage_users: bool = False
    can_view_reports: bool = False


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    can_assign_tasks: Optional[bool] = None
    can_create_tasks: Optional[bool] = None
    can_review_quality: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_view_reports: Optional[bool] = None


class RoleResponse(RoleBase):
    role_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    permission_id: int
    code: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class RolePermissionAssign(BaseModel):
    permission_codes: List[str]
