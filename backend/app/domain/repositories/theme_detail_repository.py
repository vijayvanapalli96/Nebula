"""Port protocol for fetching full theme detail (richer than StoryTheme)."""
from __future__ import annotations

from typing import Protocol

from app.domain.models.theme_detail import ThemeDetail


class ThemeDetailRepository(Protocol):
    def get_by_id(self, theme_id: str) -> ThemeDetail | None:
        """Return the full ThemeDetail for the given id, or None if not found."""
        ...
