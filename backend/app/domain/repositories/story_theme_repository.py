from __future__ import annotations

from typing import Protocol

from app.domain.models.story import StoryTheme


class StoryThemeRepository(Protocol):
    def list_active(self) -> list[StoryTheme]:
        ...

    def update_image(self, theme_id: str, image_url: str) -> None:
        """Persist a new image URL for the given theme."""
        ...
