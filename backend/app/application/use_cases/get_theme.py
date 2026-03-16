"""Use case: fetch a single ThemeDetail by its id."""
from __future__ import annotations

from app.application.errors import ThemeNotFoundError
from app.domain.models.theme_detail import ThemeDetail
from app.domain.repositories.theme_detail_repository import ThemeDetailRepository


class GetThemeUseCase:
    def __init__(self, repository: ThemeDetailRepository) -> None:
        self._repository = repository

    def execute(self, theme_id: str) -> ThemeDetail:
        """Return the ThemeDetail for *theme_id*, or raise ThemeNotFoundError."""
        theme = self._repository.get_by_id(theme_id.strip())
        if theme is None:
            raise ThemeNotFoundError(f"Theme '{theme_id}' not found.")
        return theme
