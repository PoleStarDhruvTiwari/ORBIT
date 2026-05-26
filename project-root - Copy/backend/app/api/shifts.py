from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse
from app.models.shift import Shift
from app.models.user import User
from app.core.deps import get_current_active_user
from sqlalchemy import select

router = APIRouter()

@router.get("/", response_model=list[ShiftResponse])
async def list_shifts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Shift))
    shifts = result.scalars().all()
    return shifts

@router.post("/", response_model=ShiftResponse, status_code=201)
async def create_shift(
    shift_in: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.name not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    shift = Shift(**shift_in.dict(), created_by=current_user.user_id)
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    return shift