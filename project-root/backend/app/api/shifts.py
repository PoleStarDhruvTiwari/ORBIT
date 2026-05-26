from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db
from app.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse
from app.models.shift import Shift
from app.models.user import User
from app.core.permissions import require_permission

router = APIRouter()


@router.get("/", response_model=list[ShiftResponse])
async def list_shifts(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("shifts.list")),
):
    result = await db.execute(select(Shift))
    return result.scalars().all()


@router.post("/", response_model=ShiftResponse, status_code=201)
async def create_shift(
    shift_in: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("shifts.create")),
):
    shift = Shift(
        **shift_in.dict(),
        created_by=current_user.user_id,
        updated_by=current_user.user_id,
    )
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    return shift


@router.patch("/{shift_id}", response_model=ShiftResponse)
async def update_shift(
    shift_id: int,
    shift_update: ShiftUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("shifts.update")),
):
    values = shift_update.dict(exclude_unset=True)
    if values:
        values["updated_by"] = current_user.user_id
        await db.execute(update(Shift).where(Shift.shift_id == shift_id).values(**values))
        await db.commit()
    result = await db.execute(select(Shift).where(Shift.shift_id == shift_id))
    shift = result.scalar_one_or_none()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift
