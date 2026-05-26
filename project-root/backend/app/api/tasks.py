from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatusChange,
)
from app.schemas.task_comment import TaskCommentResponse, TaskCommentCreate
from app.crud import task as crud
from app.crud import task_comment as comment_crud

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    environment: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("tasks.list")),
):
    return await crud.list_tasks(
        db,
        skip=skip,
        limit=limit,
        status=status,
        task_type=task_type,
        category_id=category_id,
        priority=priority,
        environment=environment,
        search=search,
        is_active=is_active,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("tasks.get")),
):
    row = await crud.get_by_id(db, task_id)
    if row is None:
        raise HTTPException(status_code=404, detail="task_not_found")
    return row


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tasks.create")),
):
    if await crud.get_by_key(db, payload.task_key):
        raise HTTPException(status_code=409, detail="task_key_exists")
    task = await crud.create(db, payload, actor_id=current_user.user_id)
    await comment_crud.create(
        db,
        TaskCommentCreate(task_id=task.task_id, kind="created", body=None),
        author_id=current_user.user_id,
    )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tasks.update")),
):
    row = await crud.update_task(db, task_id, payload, actor_id=current_user.user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="task_not_found")
    return row


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tasks.delete")),
):
    if not await crud.get_by_id(db, task_id):
        raise HTTPException(status_code=404, detail="task_not_found")
    await crud.soft_delete(db, task_id, actor_id=current_user.user_id)


@router.post("/{task_id}/status", response_model=TaskResponse)
async def change_status(
    task_id: int,
    change: TaskStatusChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tasks.change_status")),
):
    existing = await crud.get_by_id(db, task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="task_not_found")
    if existing.status == change.status:
        return existing
    updated = await crud.set_status(db, task_id, change.status, actor_id=current_user.user_id)
    await comment_crud.create(
        db,
        TaskCommentCreate(
            task_id=task_id,
            kind="status_change",
            body=change.comment,
            status_from=existing.status,
            status_to=change.status,
        ),
        author_id=current_user.user_id,
    )
    return updated


@router.post("/{task_id}/replicate", response_model=TaskResponse, status_code=201)
async def replicate_task(
    task_id: int,
    new_task_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tasks.replicate")),
):
    if await crud.get_by_key(db, new_task_key):
        raise HTTPException(status_code=409, detail="task_key_exists")
    cloned = await crud.replicate(db, task_id, current_user.user_id, new_task_key)
    if cloned is None:
        raise HTTPException(status_code=404, detail="task_not_found")
    return cloned


@router.get("/{task_id}/comments", response_model=list[TaskCommentResponse])
async def list_task_comments(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("task_comments.list")),
):
    return await comment_crud.list_for_task(db, task_id, skip=skip, limit=limit)


@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=201)
async def add_task_comment(
    task_id: int,
    payload: TaskCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("task_comments.create")),
):
    # path task_id is authoritative
    payload = payload.copy(update={"task_id": task_id})
    return await comment_crud.create(db, payload, author_id=current_user.user_id)
