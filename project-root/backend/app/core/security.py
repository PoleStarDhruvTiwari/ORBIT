from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.config import settings
import hashlib
import hmac
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token():
    return secrets.token_urlsafe(64)

def verify_refresh_token(token: str):
    # No JWT decode – refresh tokens are opaque and stored in DB
    return token

def hash_token(token: str):
    # Refresh tokens are 64-byte random strings (>512 bits of entropy), which
    # already exceeds bcrypt's 72-byte input limit. SHA-256 is the standard
    # choice for hashing high-entropy opaque tokens at rest.
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def verify_token(token: str, hashed: str):
    return hmac.compare_digest(hash_token(token), hashed)