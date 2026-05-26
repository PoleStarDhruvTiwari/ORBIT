from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.database import get_db
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionResponse,
    RolePermissionAssign,
)
from app.models.role import Role
from app.models.permission import Permission, RolePermission
from app.models.user import User
from app.core.permissions import require_permission

router = APIRouter()


@router.get("/", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("roles.list")),
):
    result = await db.execute(select(Role))
    return result.scalars().all()


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles.create")),
):
    role = Role(
        **role_in.dict(),
        created_by=current_user.user_id,
        updated_by=current_user.user_id,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles.update")),
):
    values = role_update.dict(exclude_unset=True)
    if not values:
        result = await db.execute(select(Role).where(Role.role_id == role_id))
        existing = result.scalar_one_or_none()
        if not existing:
            raise HTTPException(status_code=404, detail="Role not found")
        return existing
    values["updated_by"] = current_user.user_id
    await db.execute(update(Role).where(Role.role_id == role_id).values(**values))
    await db.commit()
    result = await db.execute(select(Role).where(Role.role_id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("permissions.list")),
):
    result = await db.execute(select(Permission).order_by(Permission.code))
    return result.scalars().all()


@router.get("/{role_id}/permissions", response_model=list[PermissionResponse])
async def list_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("permissions.list")),
):
    stmt = (
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.permission_id)
        .where(RolePermission.role_id == role_id, RolePermission.is_active.is_(True))
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/{role_id}/permissions", response_model=list[PermissionResponse])
async def set_role_permissions(
    role_id: int,
    body: RolePermissionAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("permissions.assign")),
):
    role = (await db.execute(select(Role).where(Role.role_id == role_id))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    perms = (
        await db.execute(
            select(Permission).where(
                Permission.code.in_(body.permission_codes),
                Permission.is_active.is_(True),
            )
        )
    ).scalars().all()
    found_codes = {p.code for p in perms}
    missing = set(body.permission_codes) - found_codes
    if missing:
        raise HTTPException(
            status_code=400, detail=f"unknown_permissions:{','.join(sorted(missing))}"
        )

    # Replace the role's permission set.
    await db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
    for p in perms:
        db.add(
            RolePermission(
                role_id=role_id,
                permission_id=p.permission_id,
                created_by=current_user.user_id,
                updated_by=current_user.user_id,
            )
        )
    await db.commit()
    return perms
