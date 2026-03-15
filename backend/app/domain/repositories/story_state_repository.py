from __future__ import annotations

from typing import Protocol

from app.domain.models.story import StoryState


class StoryStateRepository(Protocol):
    def create(self, state: StoryState) -> None:
        ...

    def get(self, session_id: str) -> StoryState | None:
        ...

    def save(self, state: StoryState) -> None:
        ...

    def list_all(self) -> list[StoryState]:
        ...

