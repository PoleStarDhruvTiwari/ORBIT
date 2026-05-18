from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.shift import Shift

async def get_shift_by_id(db: AsyncSession, shift_id: UUID):
    result = await db.execute(select(Shift).where(Shift.shift_id == shift_id))
    return result.scalar_one_or_none()