from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.settings import AIOptionsOut, UserSettingsOut, UserSettingsUpdate
from app.services.ai_service import PROVIDERS, RESPONSE_STYLES, SUPPORTED_MODELS, provider_available
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings")


@router.get("/", response_model=UserSettingsOut)
async def get_settings(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = SettingsService(db)
    return await service.get_for_user(current_user.id)


@router.put("/", response_model=UserSettingsOut)
async def update_settings(
    payload: UserSettingsUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)
    try:
        return await service.update(current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/ai-options", response_model=AIOptionsOut)
async def get_ai_options(current_user=Depends(get_current_user)):
    """Safe AI choices for the UI. Availability reflects server config only —
    no API keys or secrets are ever returned."""
    return {
        "providers": list(PROVIDERS),
        "models": SUPPORTED_MODELS,
        "response_styles": list(RESPONSE_STYLES),
        "availability": {name: provider_available(name) for name in PROVIDERS},
    }
