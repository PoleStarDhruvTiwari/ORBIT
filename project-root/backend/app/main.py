from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.router import api_router
from app.database import engine, Base
from app.core.logger import logger

app = FastAPI(title="Shift Management API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        # Create tables (for dev only; use migrations in prod)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

@app.get("/health")
async def health():
    return {"status": "ok"}