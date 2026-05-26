from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud.user import (
    get_user_by_id,
    get_user_by_email,
    create_user,
    update_user,
    delete_user,
)
from app.core.deps import get_current_active_user
from app.core.permissions import require_permission
from app.models.user import User
from app.models.role import Role

router = APIRouter()


def _to_response(u: User) -> UserResponse:
    return UserResponse(
        user_id=u.user_id,
        email=u.email,
        name=u.name,
        labeller_id=u.labeller_id,
        role=u.role.name if u.role else "",
        shift_id=u.shift_id,
        is_approved=u.is_approved,
        is_active=u.is_active,
        created_at=u.created_at,
        updated_at=u.updated_at,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_permission("users.me")),
):
    return _to_response(current_user)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("users.list")),
):
    query = select(User).options(selectinload(User.role))
    if role:
        query = query.join(User.role).where(Role.name == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return [_to_response(u) for u in result.scalars().all()]


@router.post("/", response_model=UserResponse, status_code=201)
async def create_new_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users.create")),
):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="email_already_registered")
    user = await create_user(db, user_in, created_by=current_user.user_id)
    return _to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_existing_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Self-update is allowed; otherwise require users.update permission.
    if current_user.user_id != user_id:
        # Inline permission check to avoid a second user lookup.
        from app.core.permissions import _user_permission_codes  # type: ignore
        if not (current_user.role and current_user.role.name == "super_admin"):
            codes = await _user_permission_codes(db, current_user)
            if "users.update" not in codes:
                raise HTTPException(status_code=403, detail="missing_permission:users.update")

    updated = await update_user(db, user_id, user_update, updated_by=current_user.user_id)
    return _to_response(updated)


@router.delete("/{user_id}", status_code=204)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("users.delete")),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_user(db, user_id)
