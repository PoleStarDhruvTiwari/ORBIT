from fastapi import APIRouter
from app.api import (
    auth,
    users,
    roles,
    shifts,
    task_categories,
    tasks,
    recorder_assignments,
    recording_logs,
    task_replications,
    qa_feedback,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(shifts.router, prefix="/shifts", tags=["shifts"])
api_router.include_router(
    task_categories.router, prefix="/task-categories", tags=["task-categories"]
)
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(
    recorder_assignments.router, prefix="/assignments", tags=["assignments"]
)
api_router.include_router(recording_logs.router, prefix="/recordings", tags=["recordings"])
api_router.include_router(
    task_replications.router, prefix="/task-replications", tags=["task-replications"]
)
api_router.include_router(qa_feedback.router, prefix="/qa-feedback", tags=["qa-feedback"])
