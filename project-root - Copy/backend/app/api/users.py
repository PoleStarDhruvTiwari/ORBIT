from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud.user import get_user_by_id, get_user_by_email, create_user, update_user, delete_user
from app.core.deps import get_current_active_user
from app.models.user import User
from app.core.logger import logger

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        labeller_id=current_user.labeller_id,
        role=current_user.role.name,
        shift_id=current_user.shift_id,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check permissions (role-based)
    if current_user.role.name not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    # Build query (simplified, you can expand with filters)
    from sqlalchemy import select
    from app.models.user import User
    query = select(User)
    if role:
        query = query.join(User.role).where(User.role.name == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return [UserResponse(
        user_id=u.user_id, email=u.email, name=u.name,
        labeller_id=u.labeller_id, role=u.role.name,
        shift_id=u.shift_id, is_active=u.is_active,
        created_at=u.created_at, updated_at=u.updated_at
    ) for u in users]

@router.post("/", response_model=UserResponse, status_code=201)
async def create_new_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.name not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, user_in, created_by=current_user.user_id)
    return UserResponse(
        user_id=user.user_id, email=user.email, name=user.name,
        labeller_id=user.labeller_id, role=user.role.name,
        shift_id=user.shift_id, is_active=user.is_active,
        created_at=user.created_at, updated_at=user.updated_at
    )

@router.patch("/{user_id}", response_model=UserResponse)
async def update_existing_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Permission check
    if current_user.user_id != user_id and current_user.role.name not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    updated = await update_user(db, user_id, user_update, updated_by=current_user.user_id)
    return UserResponse(
        user_id=updated.user_id, email=updated.email, name=updated.name,
        labeller_id=updated.labeller_id, role=updated.role.name,
        shift_id=updated.shift_id, is_active=updated.is_active,
        created_at=updated.created_at, updated_at=updated.updated_at
    )

@router.delete("/{user_id}", status_code=204)
async def delete_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.name not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_user(db, user_id)