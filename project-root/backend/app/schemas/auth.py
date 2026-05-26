from pydantic import BaseModel
from typing import Optional


class GoogleAuth(BaseModel):
    id_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    access_token: str
    expires_in: int


class UserSessionInfo(BaseModel):
    user_id: int
    email: str
    name: str
    role: str
    shift_id: Optional[int]
    is_approved: bool
    is_active: bool
