from __future__ import annotations

from typing import Protocol

from app.domain.models.story import StoryTheme


class StoryThemeRepository(Protocol):
    def list_active(self) -> list[StoryTheme]:
        ...
