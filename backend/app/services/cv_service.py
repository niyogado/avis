import os
from pathlib import Path
from fastapi import UploadFile
from app.config.settings import settings
from app.repositories.cv import CVRepository


class CVService:
    def __init__(self, db):
        self.repo = CVRepository(db)
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    async def save_cv(self, user_id, upload: UploadFile):
        filename = upload.filename
        dest_path = os.path.join(settings.UPLOAD_DIR, f"{user_id}_{filename}")
        with open(dest_path, "wb") as f:
            content = await upload.read()
            f.write(content)
        size = str(len(content))
        content_type = upload.content_type
        cv = await self.repo.create(user_id=user_id, filename=filename, path=dest_path, content_type=content_type, size=size)
        return cv
