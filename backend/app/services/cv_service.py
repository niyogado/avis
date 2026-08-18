import os
from pathlib import Path
from fastapi import UploadFile
from app.config.settings import settings
from app.repositories.cv import CVRepository
from app.utils.storage import Storage
from io import BytesIO


class CVService:
    def __init__(self, db):
        self.repo = CVRepository(db)
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        self.storage = Storage()

    async def save_cv(self, user_id, filename: str, content: bytes, content_type: str | None = None):
        size = str(len(content))

        # Use BytesIO for storage adapter which expects file-like
        fileobj = BytesIO(content)
        dest_name = f"{user_id}_{filename}"
        path_or_url = self.storage.save(fileobj, dest_name, content_type=content_type)

        cv = await self.repo.create(user_id=user_id, filename=filename, path=path_or_url, content_type=content_type, size=size)
        return cv
