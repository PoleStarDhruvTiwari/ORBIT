from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role


async def get_role_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def get_role_by_id(db: AsyncSession, role_id: int):
    result = await db.execute(select(Role).where(Role.role_id == role_id))
    return result.scalar_one_or_none()
