from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.crud.role import get_role_by_id

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.user_id == user_id)
    )

    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate, created_by: UUID = None):
    # Validate role exists
    role = await get_role_by_id(db, user.role_id)
    if not role:
        raise ValueError("Invalid role_id")
    db_user = User(
        email=user.email,
        name=user.name,
        labeller_id=user.labeller_id,
        role_id=user.role_id,
        shift_id=user.shift_id,
        created_by=created_by
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: UUID, user_update: UserUpdate, updated_by: UUID = None):
    stmt = update(User).where(User.user_id == user_id).values(**user_update.dict(exclude_unset=True), updated_by=updated_by)
    await db.execute(stmt)
    await db.commit()
    return await get_user_by_id(db, user_id)

async def delete_user(db: AsyncSession, user_id: UUID):
    await db.execute(update(User).where(User.user_id == user_id).values(is_active=False))
    await db.commit()