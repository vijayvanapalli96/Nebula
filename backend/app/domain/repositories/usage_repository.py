from __future__ import annotations

from typing import Protocol

from app.domain.models.composition import GenerationUsage


class UsageRepository(Protocol):
    def add_usage(self, usage: GenerationUsage) -> None:
        ...

    def get_usage(self) -> GenerationUsage:
        ...

