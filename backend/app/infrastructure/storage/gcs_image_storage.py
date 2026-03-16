from __future__ import annotations

import asyncio
import datetime
import logging
import os
from functools import partial
from pathlib import Path

from google.cloud import storage
from google.oauth2 import service_account

from app.application.ports.image_storage import ImageStoragePort
from app.core.settings import Settings

logger = logging.getLogger(__name__)

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
                # Fall back to Application Default Credentials (Cloud Run / GCE)
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

        # 1️⃣ Explicit SA key — best option, always works
        if self._signing_credentials:
            return blob.generate_signed_url(
                expiration=_SIGNED_URL_EXPIRY,
                method="GET",
                credentials=self._signing_credentials,
            )

        # 2️⃣ ADC-based signing — works on Cloud Run when the service account
        #   has roles/iam.serviceAccountTokenCreator on itself
        try:
            import google.auth
            import google.auth.transport.requests as google_requests

            adc_creds, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            adc_creds.refresh(google_requests.Request())
            service_account_email: str = getattr(adc_creds, "service_account_email", "")
            access_token: str = getattr(adc_creds, "token", "")

            if service_account_email and access_token:
                return blob.generate_signed_url(
                    expiration=_SIGNED_URL_EXPIRY,
                    method="GET",
                    service_account_email=service_account_email,
                    access_token=access_token,
                    version="v4",
                )
        except Exception:
            logger.warning(
                "ADC-based signed URL generation failed for '%s', falling back to public URL.",
                destination_path,
                exc_info=True,
            )

        # 3️⃣ Last resort: unauthenticated public URL (only works if bucket is public)
        logger.warning(
            "Returning public_url for '%s'. Ensure bucket '%s' has allUsers Storage Object Viewer "
            "or set GCS_SA_KEY_PATH / grant roles/iam.serviceAccountTokenCreator.",
            destination_path,
            self._bucket_name,
        )
        return blob.public_url
