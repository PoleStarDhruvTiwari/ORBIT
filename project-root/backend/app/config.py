from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GOOGLE_CLIENT_ID: str
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()