from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileCreate, ProfileOut

router = APIRouter(prefix="/profile")


@router.get("/", response_model=ProfileOut)
async def get_profile(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    profile = await service.get_profile_for_user(current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/", response_model=ProfileOut)
async def update_profile(payload: ProfileCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    profile = await service.upsert_profile(current_user.id, payload)
    return profile
