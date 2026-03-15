from __future__ import annotations

from typing import Any

from app.domain.models.story import StoryTheme
from app.domain.repositories.story_theme_repository import StoryThemeRepository


class FirestoreStoryThemeRepository(StoryThemeRepository):
    """
    Firestore-backed theme repository.
    Collection shape (document id = theme id):
      title, tagline, description, image, accent_color, is_active, sort_order
    """

    def __init__(self, firestore_client: Any, collection_name: str) -> None:
        self._collection = firestore_client.collection(collection_name)

    def list_active(self) -> list[StoryTheme]:
        themes: list[StoryTheme] = []
        for document in self._collection.order_by("sort_order").stream():
            payload = document.to_dict() or {}
            theme = self._to_theme(theme_id=document.id, payload=payload)
            if theme is not None and theme.is_active:
                themes.append(theme)
        return themes

    @staticmethod
    def _to_theme(theme_id: str, payload: dict[str, Any]) -> StoryTheme | None:
        title = str(payload.get("title", "")).strip()
        tagline = str(payload.get("tagline", "")).strip()
        description = str(payload.get("description", "")).strip()
        image = str(payload.get("image", "")).strip()
        accent_color = str(payload.get("accent_color", "")).strip()
        is_active = bool(payload.get("is_active", True))

        if not title or not tagline or not description or not image or not accent_color:
            return None

        sort_order_raw = payload.get("sort_order", 0)
        try:
            sort_order = int(sort_order_raw)
        except (TypeError, ValueError):
            sort_order = 0

        return StoryTheme(
            theme_id=theme_id,
            title=title,
            tagline=tagline,
            description=description,
            image=image,
            accent_color=accent_color,
            is_active=is_active,
            sort_order=sort_order,
        )
