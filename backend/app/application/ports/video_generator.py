from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VideoGenerationRequest:
    prompt: str
    model: str
    duration_seconds: int = 4
    aspect_ratio: str = "16:9"
    negative_prompt: str | None = None


@dataclass(frozen=True)
class VideoGenerationResult:
    video_bytes: bytes
    file_size_bytes: int
    duration_seconds: int


class VideoGeneratorPort(Protocol):
    async def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        ...
