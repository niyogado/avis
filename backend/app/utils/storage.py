import os
from typing import BinaryIO
from urllib.parse import urljoin

from app.config.settings import settings


class StorageError(Exception):
    pass


class Storage:
    def __init__(self):
        self.s3_enabled = settings.S3_ENABLED
        if self.s3_enabled:
            import boto3

            session = boto3.session.Session(
                aws_access_key_id=settings.S3_ACCESS_KEY or None,
                aws_secret_access_key=settings.S3_SECRET_KEY or None,
                region_name=settings.S3_REGION or None,
            )
            self.s3 = session.client("s3")
            self.bucket = settings.S3_BUCKET

    def save(self, fileobj: BinaryIO, dest_name: str, content_type: str | None = None) -> str:
        if self.s3_enabled:
            return self._save_s3(fileobj, dest_name, content_type)
        return self._save_local(fileobj, dest_name)

    def _save_local(self, fileobj: BinaryIO, dest_name: str) -> str:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        dest_path = os.path.join(settings.UPLOAD_DIR, dest_name)
        # fileobj is binary content
        with open(dest_path, "wb") as f:
            f.write(fileobj.read())
        return dest_path

    def _save_s3(self, fileobj: BinaryIO, dest_name: str, content_type: str | None = None) -> str:
        if not self.bucket:
            raise StorageError("S3 bucket not configured")
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        # reset fileobj pointer
        fileobj.seek(0)
        self.s3.upload_fileobj(fileobj, self.bucket, dest_name, ExtraArgs=extra_args)
        url = f"https://{self.bucket}.s3.{settings.S3_REGION}.amazonaws.com/{dest_name}"
        return url

    def read(self, stored_path: str) -> bytes:
        if stored_path.startswith('http://') or stored_path.startswith('https://'):
            raise StorageError("Remote CV files cannot be read from this storage backend yet.")
        if not os.path.isfile(stored_path):
            raise StorageError("The original CV file is no longer available on disk.")
        with open(stored_path, "rb") as handle:
            return handle.read()
