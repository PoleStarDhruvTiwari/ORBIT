from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.models.role import Role
from app.models.user import User
from app.core.deps import get_current_active_user
from sqlalchemy import select

router = APIRouter()

@router.get("/", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.name != "super_admin":
        raise HTTPException(status_code=403, detail="Only super_admin can view roles")
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return roles

@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.name != "super_admin":
        raise HTTPException(status_code=403, detail="Only super_admin can create roles")
    role = Role(**role_in.dict(), created_by=current_user.user_id)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role