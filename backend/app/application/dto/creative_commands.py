from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.models.composition import MediaPartType


@dataclass(frozen=True)
class CreateProjectCommand:
    title: str
    use_case: str
    tone: str | None = None
    style_bible: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CreateCompositionCommand:
    prompt: str
    target_platform: str
    project_id: str | None = None
    requested_modalities: list[MediaPartType] = field(default_factory=lambda: ["text", "image"])
    max_parts: int = 8


@dataclass(frozen=True)
class RegenerateCompositionPartCommand:
    composition_id: str
    part_id: str
    instruction: str | None = None


@dataclass(frozen=True)
class CreateAssetUploadCommand:
    filename: str
    mime_type: str
    expires_in_minutes: int = 30


@dataclass(frozen=True)
class ExportCompositionCommand:
    composition_id: str
    export_format: str

