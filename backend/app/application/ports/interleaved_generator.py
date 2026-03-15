from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.domain.models.composition import CompositionPart, GenerationUsage, MediaPartType


@dataclass(frozen=True)
class InterleavedGenerationRequest:
    prompt: str
    requested_modalities: list[MediaPartType]
    style_bible: dict[str, Any] = field(default_factory=dict)
    max_parts: int = 8


@dataclass(frozen=True)
class InterleavedGenerationResult:
    parts: list[CompositionPart]
    usage: GenerationUsage


class InterleavedGeneratorPort(Protocol):
    async def generate(self, request: InterleavedGenerationRequest) -> InterleavedGenerationResult:
        ...

    async def regenerate_part(
        self,
        request: InterleavedGenerationRequest,
        original_part: CompositionPart,
        instruction: str | None = None,
    ) -> CompositionPart:
        ...

