from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

VideoStatus = Literal["queued", "generating", "completed", "failed"]
AspectRatio = Literal["16:9", "9:16", "1:1"]


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class VideoJob:
    job_id: str
    prompt: str
    model: str
    status: VideoStatus
    duration_seconds: int = 4
    aspect_ratio: str = "16:9"
    negative_prompt: str | None = None
    video_uri: str | None = None
    mime_type: str = "video/mp4"
    file_size_bytes: int = 0
    cost_estimate: float = 0.0
    error_message: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
