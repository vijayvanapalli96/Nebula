from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VideoJobResult:
    job_id: str
    status: str
    prompt: str
    model: str
    duration_seconds: int
    aspect_ratio: str
    video_uri: str | None
    file_size_bytes: int
    cost_estimate: float
    error_message: str | None
    created_at: datetime
    updated_at: datetime
