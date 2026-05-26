from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.router import api_router
from app.core.logger import logger
from app.core.migrate import run_migrations
from app.core.permissions import sync_permissions
from app.core.exceptions import install_exception_handlers

app = FastAPI(title="Shift Management API")

install_exception_handlers(app)

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
async def on_startup():
    # 1) Apply sql/schema.sql -> sql/seed.sql -> sql/alter.sql.
    #    Idempotent; safe to run on every boot.
    try:
        await run_migrations()
        logger.info("SQL migrations applied")
    except Exception as e:
        logger.exception(f"SQL migration failed: {e}")
        # Don't continue with sync_permissions if the schema isn't in place.
        return

    # 2) Reconcile the in-code permissions registry with the DB.
    try:
        await sync_permissions()
        logger.info("Permissions synced")
    except Exception as e:
        logger.exception(f"Permission sync failed: {e}")


@app.get("/health")
async def health():
    return {"status": "ok"}
