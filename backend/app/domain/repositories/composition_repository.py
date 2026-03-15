from __future__ import annotations

from typing import Protocol

from app.domain.models.composition import Composition


class CompositionRepository(Protocol):
    def create(self, composition: Composition) -> None:
        ...

    def get(self, composition_id: str) -> Composition | None:
        ...

    def save(self, composition: Composition) -> None:
        ...

    def list_all(self) -> list[Composition]:
        ...

