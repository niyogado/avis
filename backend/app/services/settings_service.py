from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_settings import UserSettings
from app.schemas.settings import UserSettingsUpdate
from app.services.ai_service import SUPPORTED_MODELS


class SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_for_user(self, user_id) -> UserSettings:
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        if settings is None:
            settings = UserSettings(user_id=user_id)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings

    async def update(self, user_id, payload: UserSettingsUpdate) -> UserSettings:
        settings = await self.get_for_user(user_id)
        data = payload.model_dump()

        # Cross-field validation: the chosen model must belong to the chosen
        # provider (Auto has no models of its own).
        provider = data["ai_provider"]
        model = data["ai_model"]
        allowed = SUPPORTED_MODELS.get(provider, [])
        if provider == "auto":
            data["ai_model"] = ""
        elif model and model not in allowed:
            raise ValueError(f"Model '{model}' is not supported by provider '{provider}'.")
        elif not model and allowed:
            data["ai_model"] = allowed[0]

        for key, value in data.items():
            setattr(settings, key, value)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def resolve_ai_options(self, user_id) -> dict:
        """Return the provider/model/style/fallback kwargs for an AI call."""
        settings = await self.get_for_user(user_id)
        return {
            "provider": settings.ai_provider,
            "model": settings.ai_model or None,
            "style": settings.ai_response_style,
            "allow_fallback": settings.ai_fallback_enabled,
        }
