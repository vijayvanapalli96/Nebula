"""In-memory tracker for background media-generation tasks.

Stores only lightweight metadata (status + GCS URI per asset).
Actual media bytes live in GCS — nothing heavy is kept in memory.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class AssetStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AssetState:
    asset_key: str
    asset_type: str  # "image" or "video"
    prompt: str
    status: AssetStatus = AssetStatus.PENDING
    uri: str | None = None
    error: str | None = None


@dataclass
class MediaRequest:
    request_id: str
    assets: dict[str, AssetState] = field(default_factory=dict)

    @property
    def completed(self) -> bool:
        return all(a.status != AssetStatus.PENDING for a in self.assets.values())

    @property
    def summary(self) -> dict[str, Any]:
        total = len(self.assets)
        done = sum(1 for a in self.assets.values() if a.status == AssetStatus.COMPLETED)
        failed = sum(1 for a in self.assets.values() if a.status == AssetStatus.FAILED)
        pending = total - done - failed
        return {
            "request_id": self.request_id,
            "total": total,
            "completed": done,
            "failed": failed,
            "pending": pending,
            "done": self.completed,
            "assets": {
                k: {
                    "asset_type": v.asset_type,
                    "status": v.status.value,
                    "uri": v.uri,
                    "error": v.error,
                }
                for k, v in self.assets.items()
            },
        }


class MediaTaskTracker:
    """Thread-safe tracker for background media generation tasks."""

    def __init__(self) -> None:
        self._requests: dict[str, MediaRequest] = {}

    def create_request(self, assets: list[AssetState]) -> str:
        """Register a new media request and return its ID."""
        request_id = str(uuid4())
        media_req = MediaRequest(request_id=request_id)
        for asset in assets:
            media_req.assets[asset.asset_key] = asset
        self._requests[request_id] = media_req
        logger.info("Created media request %s with %d assets", request_id, len(assets))
        return request_id

    def mark_completed(self, request_id: str, asset_key: str, uri: str) -> None:
        req = self._requests.get(request_id)
        if req and asset_key in req.assets:
            req.assets[asset_key].status = AssetStatus.COMPLETED
            req.assets[asset_key].uri = uri
            logger.info("Asset %s completed: %s", asset_key, uri)

    def mark_failed(self, request_id: str, asset_key: str, error: str) -> None:
        req = self._requests.get(request_id)
        if req and asset_key in req.assets:
            req.assets[asset_key].status = AssetStatus.FAILED
            req.assets[asset_key].error = error
            logger.warning("Asset %s failed: %s", asset_key, error)

    def get_status(self, request_id: str) -> dict[str, Any] | None:
        req = self._requests.get(request_id)
        if req is None:
            return None
        return req.summary


# Module-level singleton
_tracker = MediaTaskTracker()


def get_media_tracker() -> MediaTaskTracker:
    return _tracker
