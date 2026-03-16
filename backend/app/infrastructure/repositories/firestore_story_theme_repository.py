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
        for document in self._collection.stream():
            payload = document.to_dict() or {}
            theme = self._to_theme(document_id=document.id, payload=payload)
            if theme is not None and theme.is_active:
                themes.append(theme)
        return sorted(themes, key=lambda item: item.sort_order)

    def update_image(self, theme_id: str, image_url: str) -> None:
        """Update the image field for a theme document in Firestore."""
        self._collection.document(theme_id).update({"image": image_url})

    @staticmethod
    def _to_theme(document_id: str, payload: dict[str, Any]) -> StoryTheme | None:
        title = _first_non_empty(payload, "title")
        description = _first_non_empty(payload, "description")
        if not title or not description:
            return None

        # Supports both current and legacy schemas.
        theme_id = _first_non_empty(payload, "themeId", "theme_id", default=document_id)
        category = _first_non_empty(payload, "category")
        tagline = _first_non_empty(
            payload,
            "tagline",
            "subtitle",
            default=category or f"Immerse yourself in {title}.",
        )
        image = _first_non_empty(payload, "image", "heroImageUrl", "thumbnailUrl")
        if not image:
            image = _image_for_category(category)

        accent_color = _first_non_empty(payload, "accent_color", "accentColor")
        if not accent_color:
            accent_color = _accent_for_category(category)

        is_active = bool(payload.get("is_active", payload.get("active", True)))

        sort_order_raw = payload.get(
            "sort_order",
            payload.get("sortOrder", payload.get("popularityScore", 0)),
        )
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


def _first_non_empty(payload: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def _accent_for_category(category: str) -> str:
    token = category.strip().lower()
    mapping = {
        "mystery": "rgba(234,179,8,0.6)",
        "sci-fi": "rgba(59,130,246,0.6)",
        "thriller": "rgba(239,68,68,0.6)",
        "fantasy": "rgba(168,85,247,0.6)",
        "survival": "rgba(249,115,22,0.6)",
        "political": "rgba(20,184,166,0.6)",
        "mythology": "rgba(217,119,6,0.6)",
        "supernatural": "rgba(129,140,248,0.6)",
    }
    return mapping.get(token, "rgba(124,58,237,0.6)")


def _image_for_category(category: str) -> str:
    token = category.strip().lower()
    mapping = {
        "mystery": "https://images.unsplash.com/photo-1605806616949-1e87b487fc2f?w=800&q=80",
        "sci-fi": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&q=80",
        "thriller": "https://images.unsplash.com/photo-1518895312237-a9e23508077d?w=800&q=80",
        "fantasy": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80",
        "survival": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        "political": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80",
        "mythology": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=800&q=80",
        "supernatural": "https://images.unsplash.com/photo-1511497584788-876760111969?w=800&q=80",
    }
    return mapping.get(token, "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80")
