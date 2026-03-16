from __future__ import annotations

from typing import Protocol


class ImageStoragePort(Protocol):
    async def upload_image(self, image_bytes: bytes, destination_path: str) -> str:
        """Upload image bytes and return an accessible URL."""
        ...

    async def upload_video(self, video_bytes: bytes, destination_path: str) -> str:
        """Upload video bytes and return an accessible URL."""
        ...

    async def url_for(self, gcs_path: str) -> str:
        """Return an accessible URL for an existing GCS object path.

        If gcs_path is already an https:// URL it is returned unchanged.
        Otherwise a signed URL (or public URL fallback) is generated.
        """
        ...
