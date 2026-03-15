from __future__ import annotations

from typing import Protocol


class ImageStoragePort(Protocol):
    async def upload_image(self, image_bytes: bytes, destination_path: str) -> str:
        """Upload image bytes and return a public URL."""
        ...
