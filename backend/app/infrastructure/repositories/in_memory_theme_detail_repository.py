"""In-memory ThemeDetailRepository for local development / tests."""
from __future__ import annotations

from app.domain.models.theme_detail import ThemeDetail
from app.domain.repositories.theme_detail_repository import ThemeDetailRepository


class InMemoryThemeDetailRepository:
    """Simple dict-backed repository seeded with no themes by default."""

    def __init__(self, themes: dict[str, ThemeDetail] | None = None) -> None:
        self._store: dict[str, ThemeDetail] = themes or {}

    def get_by_id(self, theme_id: str) -> ThemeDetail | None:
        return self._store.get(theme_id)

    def add(self, theme: ThemeDetail) -> None:
        """Utility for tests: seed a theme."""
        self._store[theme.theme_id] = theme
