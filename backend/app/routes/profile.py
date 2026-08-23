from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.profile_service import ProfileService
from app.schemas.profile import (
    ProfileCreate,
    ProfileOut,
    ProfessionalContextOut,
    ProfessionalContextPayload,
)

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


@router.get("/professional-context", response_model=ProfessionalContextOut)
async def get_professional_context_api(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProfileService(db)
    context = await service.get_professional_context(current_user.id)
    if not context:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No confirmed professional context yet")
    return context


@router.put("/professional-context", response_model=ProfessionalContextOut)
async def save_professional_context_api(
    payload: ProfessionalContextPayload,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Persist USER-CONFIRMED professional identity from the CV Editor."""
    service = ProfileService(db)
    confirmed = await service.save_professional_context(current_user.id, payload)
    return confirmed
