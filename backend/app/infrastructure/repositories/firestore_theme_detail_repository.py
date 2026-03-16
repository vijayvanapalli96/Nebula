"""Firestore-backed ThemeDetailRepository.

Reads from the ``themes`` collection and maps Firestore documents to ThemeDetail
domain objects. Supports both camelCase (seeded docs) and snake_case field names.
"""
from __future__ import annotations

from typing import Any

from app.domain.models.theme_detail import PromptHints, ThemeDetail
from app.domain.repositories.theme_detail_repository import ThemeDetailRepository


class FirestoreThemeDetailRepository:
    """Fetch individual theme documents from Firestore."""

    def __init__(self, firestore_client: Any, collection_name: str = "themes") -> None:
        self._collection = firestore_client.collection(collection_name)

    def get_by_id(self, theme_id: str) -> ThemeDetail | None:
        doc_ref = self._collection.document(theme_id)
        snapshot = doc_ref.get()
        if not snapshot.exists:
            return None
        payload: dict[str, Any] = snapshot.to_dict() or {}
        return self._to_theme_detail(
            theme_id=snapshot.id,
            payload=payload,
        )

    @staticmethod
    def _to_theme_detail(theme_id: str, payload: dict[str, Any]) -> ThemeDetail:
        hints_raw: dict[str, Any] = payload.get(
            "promptHints", payload.get("prompt_hints", {})
        ) or {}
        hints = PromptHints(
            narrative_style=str(hints_raw.get("narrativeStyle", hints_raw.get("narrative_style", ""))).strip(),
            visual_style=str(hints_raw.get("visualStyle", hints_raw.get("visual_style", ""))).strip(),
        )

        raw_tags = payload.get("defaultToneTags", payload.get("default_tone_tags", []))
        tone_tags: tuple[str, ...] = tuple(str(t) for t in (raw_tags or []))

        # Resolve theme_id from document data or fall back to document key.
        resolved_id = str(
            payload.get("themeId", payload.get("theme_id", theme_id)) or theme_id
        ).strip()

        is_active = bool(payload.get("active", payload.get("is_active", True)))

        return ThemeDetail(
            theme_id=resolved_id,
            title=str(payload.get("title", "")).strip(),
            category=str(payload.get("category", "")).strip(),
            description=str(payload.get("description", "")).strip(),
            default_tone_tags=tone_tags,
            prompt_hints=hints,
            is_active=is_active,
        )
