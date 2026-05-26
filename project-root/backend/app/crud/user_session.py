from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone

from app.models.user_session import UserSession
from app.core.security import hash_token, verify_token


async def create_session(
    db: AsyncSession,
    user_id: int,
    refresh_token: str,
    expires_at: datetime,
    device_id: str | None = None,
    device_type: str = "web",
):
    session = UserSession(
        user_id=user_id,
        hashed_refresh_token=hash_token(refresh_token),
        expires_at=expires_at,
        device_id=device_id,
        device_type=device_type,
        last_login=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session_by_refresh_token(db: AsyncSession, refresh_token: str):
    # Hashed at rest → fetch candidates and verify.
    result = await db.execute(
        select(UserSession).where(UserSession.expires_at > datetime.now(timezone.utc))
    )
    for sess in result.scalars().all():
        if verify_token(refresh_token, sess.hashed_refresh_token):
            return sess
    return None


async def delete_session(db: AsyncSession, refresh_token: str):
    sess = await get_session_by_refresh_token(db, refresh_token)
    if sess:
        await db.execute(delete(UserSession).where(UserSession.session_id == sess.session_id))
        await db.commit()
