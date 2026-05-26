from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.task_category import (
    TaskCategoryCreate,
    TaskCategoryUpdate,
    TaskCategoryResponse,
)
from app.crud import task_category as crud

router = APIRouter()


@router.get("/", response_model=list[TaskCategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("task_categories.list")),
):
    return await crud.list_categories(db, skip=skip, limit=limit, is_active=is_active)


@router.post("/", response_model=TaskCategoryResponse, status_code=201)
async def create_category(
    payload: TaskCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("task_categories.create")),
):
    if await crud.get_by_name(db, payload.name):
        raise HTTPException(status_code=409, detail="category_name_exists")
    return await crud.create(db, payload, actor_id=current_user.user_id)


@router.patch("/{task_category_id}", response_model=TaskCategoryResponse)
async def update_category(
    task_category_id: int,
    payload: TaskCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("task_categories.update")),
):
    row = await crud.update_category(db, task_category_id, payload, actor_id=current_user.user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="task_category_not_found")
    return row
