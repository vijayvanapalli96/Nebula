from __future__ import annotations

import asyncio
import datetime
import os
from functools import partial
from pathlib import Path

from google.cloud import storage
from google.oauth2 import service_account

from app.application.ports.image_storage import ImageStoragePort
from app.core.settings import Settings

_SIGNED_URL_EXPIRY = datetime.timedelta(days=7)


class GcsImageStorage(ImageStoragePort):
    """Uploads images to a Google Cloud Storage bucket and returns signed URLs."""

    def __init__(self, settings: Settings) -> None:
        self._bucket_name = settings.gcs_bucket_name
        self._client: storage.Client | None = None
        self._signing_credentials: service_account.Credentials | None = None

        if self._bucket_name:
            sa_key = os.getenv("GCS_SA_KEY_PATH", "")
            if sa_key and Path(sa_key).exists():
                creds = service_account.Credentials.from_service_account_file(sa_key)
                self._client = storage.Client(credentials=creds, project=creds.project_id)
                self._signing_credentials = creds
            else:
                # Fall back to Application Default Credentials (no signed URLs)
                self._client = storage.Client()

    async def upload_image(self, image_bytes: bytes, destination_path: str) -> str:
        if self._client is None or not self._bucket_name:
            raise RuntimeError("GCS_BUCKET_NAME is not configured.")

        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(
            None,
            partial(self._upload_sync, image_bytes, destination_path, "image/png"),
        )
        return url

    async def upload_video(self, video_bytes: bytes, destination_path: str) -> str:
        if self._client is None or not self._bucket_name:
            raise RuntimeError("GCS_BUCKET_NAME is not configured.")

        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(
            None,
            partial(self._upload_sync, video_bytes, destination_path, "video/mp4"),
        )
        return url

    def _upload_sync(self, data: bytes, destination_path: str, content_type: str) -> str:
        bucket = self._client.bucket(self._bucket_name)  # type: ignore[union-attr]
        blob = bucket.blob(destination_path)
        blob.upload_from_string(data, content_type=content_type)

        if self._signing_credentials:
            url: str = blob.generate_signed_url(
                expiration=_SIGNED_URL_EXPIRY,
                method="GET",
                credentials=self._signing_credentials,
            )
            return url

        # Fallback: unauthenticated public URL (only works if bucket is public)
        return blob.public_url
