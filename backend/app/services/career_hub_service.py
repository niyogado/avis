from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.job_alert import JobAlert


class CareerHubService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_applications(self, user_id):
        stmt = select(Application).where(Application.user_id == user_id).order_by(Application.updated_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_application(self, user_id, payload: dict):
        application = Application(
            user_id=user_id,
            title=payload['title'],
            company=payload.get('company'),
            location=payload.get('location'),
            source_url=payload.get('source_url'),
            match_score=payload.get('match_score'),
            match_reasons=payload.get('match_reasons') or [],
            status=payload.get('status') or 'saved',
            notes=payload.get('notes'),
        )
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        return application

    async def list_alerts(self, user_id):
        stmt = select(JobAlert).where(JobAlert.user_id == user_id).order_by(JobAlert.updated_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_alert(self, user_id, payload: dict):
        alert = JobAlert(
            user_id=user_id,
            title=payload['title'],
            query=payload['query'],
            target_roles=payload.get('target_roles') or [],
            is_active=payload.get('is_active', True),
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert
