from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.crud.role import get_role_by_id


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate, created_by: int | None = None):
    role = await get_role_by_id(db, user.role_id)
    if not role:
        raise ValueError("Invalid role_id")
    db_user = User(
        email=user.email,
        name=user.name,
        labeller_id=user.labeller_id,
        role_id=user.role_id,
        shift_id=user.shift_id,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return await get_user_by_id(db, db_user.user_id)


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate,
    updated_by: int | None = None,
):
    values = user_update.dict(exclude_unset=True)
    if updated_by is not None:
        values["updated_by"] = updated_by
    if values:
        await db.execute(update(User).where(User.user_id == user_id).values(**values))
        await db.commit()
    return await get_user_by_id(db, user_id)


async def delete_user(db: AsyncSession, user_id: int):
    await db.execute(update(User).where(User.user_id == user_id).values(is_active=False))
    await db.commit()
