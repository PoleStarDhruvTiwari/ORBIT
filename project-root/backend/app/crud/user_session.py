from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user_session import UserSession
from uuid import UUID
from datetime import datetime, timedelta
import secrets

async def create_session(db: AsyncSession, user_id: UUID, refresh_token: str, expires_at: datetime, device_id: str = None, device_type: str = None):
    session = UserSession(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        device_id=device_id,
        device_type=device_type,
        last_login=datetime.utcnow()
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_session_by_refresh_token(db: AsyncSession, refresh_token: str):
    result = await db.execute(select(UserSession).where(UserSession.refresh_token == refresh_token))
    return result.scalar_one_or_none()

async def delete_session(db: AsyncSession, refresh_token: str):
    await db.execute(delete(UserSession).where(UserSession.refresh_token == refresh_token))
    await db.commit()