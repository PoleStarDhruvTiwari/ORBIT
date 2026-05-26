"""
Single source of truth for application permissions.

Every API endpoint that needs RBAC declares its permission code in PERMISSIONS
below. On application startup, `sync_permissions()` reconciles this list with
the `permissions` table:

  * codes present here but missing in DB -> inserted (is_active=TRUE)
  * codes present here AND in DB -> ensured is_active=TRUE (reactivated if
    previously removed and brought back)
  * codes present in DB but missing here -> set is_active=FALSE (never deleted)

Use `require_permission("code")` as a FastAPI dependency to gate an endpoint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal, get_db
from app.models.permission import Permission, RolePermission
from app.models.role import Role
from app.models.user import User


# ---------------------------------------------------------------------------
# Registry: add every API permission here.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PermissionDef:
    code: str
    description: str


PERMISSIONS: tuple[PermissionDef, ...] = (
    # Roles
    PermissionDef("roles.list", "List roles"),
    PermissionDef("roles.create", "Create a role"),
    PermissionDef("roles.update", "Update a role"),
    PermissionDef("roles.delete", "Delete a role"),

    # Permissions admin
    PermissionDef("permissions.list", "List permissions"),
    PermissionDef("permissions.assign", "Assign permissions to a role"),

    # Users
    PermissionDef("users.me", "View own profile"),
    PermissionDef("users.list", "List users"),
    PermissionDef("users.create", "Create a user"),
    PermissionDef("users.update", "Update a user"),
    PermissionDef("users.delete", "Deactivate a user"),
    PermissionDef("users.approve", "Approve a user"),

    # Shifts
    PermissionDef("shifts.list", "List shifts"),
    PermissionDef("shifts.create", "Create a shift"),
    PermissionDef("shifts.update", "Update a shift"),

    # Sessions
    PermissionDef("sessions.list", "List own sessions"),
    PermissionDef("sessions.revoke", "Revoke a session"),

    # Task categories
    PermissionDef("task_categories.list", "List task categories"),
    PermissionDef("task_categories.create", "Create a task category"),
    PermissionDef("task_categories.update", "Update a task category"),

    # Tasks
    PermissionDef("tasks.list", "List tasks"),
    PermissionDef("tasks.get", "Get a single task"),
    PermissionDef("tasks.create", "Create a task"),
    PermissionDef("tasks.update", "Update a task"),
    PermissionDef("tasks.delete", "Soft-delete a task"),
    PermissionDef("tasks.change_status", "Change a task's lifecycle status"),
    PermissionDef("tasks.replicate", "Replicate a task into a new draft"),

    # Task comments
    PermissionDef("task_comments.list", "List comments on a task"),
    PermissionDef("task_comments.create", "Comment on a task"),

    # Recorder assignments
    PermissionDef("assignments.list", "List all assignments"),
    PermissionDef("assignments.get", "Get any assignment"),
    PermissionDef("assignments.create", "Create an assignment"),
    PermissionDef("assignments.update", "Update any assignment"),
    PermissionDef("assignments.skip", "Skip any assignment"),
    PermissionDef("assignments.reassign", "Reassign an assignment to another recorder"),

    # Recording logs
    PermissionDef("recordings.list", "List recording logs"),
    PermissionDef("recordings.get", "Get any recording log"),
    PermissionDef("recordings.create_any", "Create a recording log on behalf of others"),
    PermissionDef("recordings.update", "Update any recording log"),
    PermissionDef("recordings.review", "Approve / reject / request-rework a recording"),

    # Task replications
    PermissionDef("task_replications.list", "List task replications"),
    PermissionDef("task_replications.create", "Create a task replication"),

    # QA feedback
    PermissionDef("qa_feedback.list", "List QA feedback"),
    PermissionDef("qa_feedback.create", "Submit QA feedback on a recording"),
    PermissionDef("qa_feedback.update", "Update QA feedback"),
)


def _code_set() -> set[str]:
    return {p.code for p in PERMISSIONS}


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

async def sync_permissions() -> None:
    """Reconcile the PERMISSIONS list with the `permissions` table.

    Idempotent. Safe to call on every startup.
    """
    declared = {p.code: p for p in PERMISSIONS}

    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(Permission))).scalars().all()
        existing_by_code = {p.code: p for p in existing}

        # Add new + reactivate any returning ones
        for code, pdef in declared.items():
            row = existing_by_code.get(code)
            if row is None:
                db.add(Permission(code=code, description=pdef.description, is_active=True))
            else:
                changed = False
                if not row.is_active:
                    row.is_active = True
                    changed = True
                if row.description != pdef.description:
                    row.description = pdef.description
                    changed = True
                if changed:
                    db.add(row)

        # Soft-delete (deactivate) ones removed from code
        for code, row in existing_by_code.items():
            if code not in declared and row.is_active:
                row.is_active = False
                db.add(row)

        await db.commit()


# ---------------------------------------------------------------------------
# Runtime check
# ---------------------------------------------------------------------------

async def _user_permission_codes(db: AsyncSession, user: User) -> set[str]:
    """Active permission codes for the given user via their role."""
    stmt = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.permission_id)
        .where(
            RolePermission.role_id == user.role_id,
            RolePermission.is_active.is_(True),
            Permission.is_active.is_(True),
        )
    )
    result = await db.execute(stmt)
    return {row[0] for row in result.all()}


def require_permission(code: str):
    """FastAPI dependency factory: enforces that the caller has `code`.

    super_admin bypasses the check.
    """
    # Imported here to avoid a circular import with core.deps
    from app.core.deps import get_current_active_user

    async def _checker(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        # super_admin bypass
        if current_user.role and current_user.role.name == "super_admin":
            return current_user

        codes = await _user_permission_codes(db, current_user)
        if code not in codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"missing_permission:{code}",
            )
        return current_user

    return _checker


def require_any_permission(codes: Iterable[str]):
    """Pass if the user has any one of the given codes."""
    from app.core.deps import get_current_active_user

    needed = set(codes)

    async def _checker(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role and current_user.role.name == "super_admin":
            return current_user
        held = await _user_permission_codes(db, current_user)
        if not (needed & held):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"missing_permission:{'|'.join(sorted(needed))}",
            )
        return current_user

    return _checker
