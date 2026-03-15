from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

MediaPartType = Literal["text", "image", "audio", "video", "caption", "cta"]
PartStatus = Literal["queued", "generating", "completed", "failed"]
CompositionStatus = Literal["queued", "generating", "partial", "completed", "failed"]
AssetStatus = Literal["pending_upload", "ready", "failed"]


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class GenerationUsage:
    prompt_tokens: int = 0
    output_tokens: int = 0
    image_count: int = 0
    audio_seconds: int = 0
    video_seconds: int = 0

    def merge(self, other: GenerationUsage) -> None:
        self.prompt_tokens += other.prompt_tokens
        self.output_tokens += other.output_tokens
        self.image_count += other.image_count
        self.audio_seconds += other.audio_seconds
        self.video_seconds += other.video_seconds


@dataclass
class CompositionPart:
    part_id: str
    type: MediaPartType
    sequence: int
    status: PartStatus
    content: str | None = None
    asset_uri: str | None = None
    mime_type: str | None = None
    duration_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Project:
    project_id: str
    title: str
    use_case: str
    tone: str | None = None
    style_bible: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Composition:
    composition_id: str
    project_id: str | None
    prompt: str
    target_platform: str
    status: CompositionStatus
    requested_modalities: list[MediaPartType]
    parts: list[CompositionPart] = field(default_factory=list)
    version: int = 1
    usage: GenerationUsage = field(default_factory=GenerationUsage)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class AssetRecord:
    asset_id: str
    filename: str
    mime_type: str
    upload_url: str
    storage_uri: str
    expires_at: datetime
    status: AssetStatus = "pending_upload"
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @staticmethod
    def expires_after(minutes: int) -> datetime:
        return utc_now() + timedelta(minutes=minutes)

