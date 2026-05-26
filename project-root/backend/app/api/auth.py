from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.database import get_db
from app.crud.user import get_user_by_id, get_user_by_email
from app.config import settings
from app.schemas.auth import GoogleAuth, Token, TokenRefresh, UserSessionInfo
from app.crud.user_session import (
    create_session,
    get_session_by_refresh_token,
    delete_session,
)
from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import UserNotRegisteredException
from app.core.logger import logger

router = APIRouter()


@router.post("/google", response_model=Token)
async def google_login(
    auth: GoogleAuth,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        info = id_token.verify_oauth2_token(
            auth.id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        email = info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="missing_email")
    except Exception as e:
        logger.error(f"Google token verification failed: {e}")
        raise HTTPException(status_code=401, detail="invalid_google_token")

    user = await get_user_by_email(db, email)
    if not user or not user.is_active:
        raise UserNotRegisteredException()

    access_token = create_access_token(data={"sub": str(user.user_id)})
    refresh_token = create_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    ua = (request.headers.get("user-agent") or "").lower()
    if "mobile" in ua:
        device_type = "mobile"
    elif "tablet" in ua:
        device_type = "tablet"
    else:
        device_type = "web"

    await create_session(
        db,
        user.user_id,
        refresh_token,
        expires_at,
        device_type=device_type,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenRefresh)
async def refresh_access_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="session_expired")

    session = await get_session_by_refresh_token(db, refresh_token)
    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="session_expired")

    new_access_token = create_access_token(data={"sub": str(session.user_id)})
    return TokenRefresh(
        access_token=new_access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/session")
async def get_session(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="session_expired")

    session = await get_session_by_refresh_token(db, refresh_token)
    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="session_expired")

    user = await get_user_by_id(db, session.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="session_expired")

    new_access_token = create_access_token(data={"sub": str(user.user_id)})

    return {
        "access_token": new_access_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserSessionInfo(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role.name if user.role else "",
            shift_id=user.shift_id,
            is_approved=user.is_approved,
            is_active=user.is_active,
        ),
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await delete_session(db, refresh_token)
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
