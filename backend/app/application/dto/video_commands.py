from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateVideoCommand:
    prompt: str
    duration_seconds: int = 4
    aspect_ratio: str = "16:9"
    model: str = "veo-3.0-fast-generate-001"
    negative_prompt: str | None = None
