from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.models.story import UserStoryRecord
from app.domain.repositories.user_story_repository import UserStoryRepository


class FirestoreUserStoryRepository(UserStoryRepository):
    """
    Firestore-backed user story repository.
    Expected path: /{users_collection}/{user_id}/{stories_subcollection}/{story_id}
    """

    def __init__(
        self,
        firestore_client: Any,
        users_collection: str,
        stories_subcollection: str,
    ) -> None:
        self._client = firestore_client
        self._users_collection = users_collection
        self._stories_subcollection = stories_subcollection

    def list_by_user_id(self, user_id: str) -> list[UserStoryRecord]:
        docs = (
            self._client.collection(self._users_collection)
            .document(user_id)
            .collection(self._stories_subcollection)
            .stream()
        )
        stories: list[UserStoryRecord] = []
        for doc in docs:
            payload = doc.to_dict() or {}
            story = _to_user_story_record(
                user_id=user_id,
                document_id=doc.id,
                payload=payload,
            )
            if story is not None:
                stories.append(story)
        return sorted(stories, key=lambda item: item.updated_at, reverse=True)

    def get_by_user_id_and_story_id(
        self,
        user_id: str,
        story_id: str,
    ) -> UserStoryRecord | None:
        doc = (
            self._client.collection(self._users_collection)
            .document(user_id)
            .collection(self._stories_subcollection)
            .document(story_id)
            .get()
        )
        if not getattr(doc, "exists", False):
            return None
        payload = doc.to_dict() or {}
        return _to_user_story_record(
            user_id=user_id,
            document_id=doc.id,
            payload=payload,
        )


def _to_user_story_record(
    user_id: str,
    document_id: str,
    payload: dict[str, Any],
) -> UserStoryRecord | None:
    story_id = _first_non_empty(payload, "storyId", "story_id", default=document_id)
    title = _first_non_empty(payload, "title", "storyTitle", "name", "themeTitle")
    if not story_id:
        return None
    if not title:
        title = f"Story {story_id}"

    session_id = _first_non_empty(payload, "sessionId", "session_id") or None
    genre = _first_non_empty(payload, "genre", "theme", "category", "themeCategory", default="Unknown")
    character_name = _first_non_empty(
        payload,
        "characterName",
        "character_name",
        "heroName",
        "protagonistName",
        default="Unknown",
    )
    archetype = _first_non_empty(payload, "archetype", "characterArchetype", default="Unknown")
    last_scene_id = _first_non_empty(
        payload,
        "lastSceneId",
        "last_scene_id",
        "currentSceneId",
        "current_scene_id",
    ) or None

    choices_available = _to_int(
        payload.get(
            "choicesAvailable",
            payload.get(
                "choices_available",
                payload.get("availableChoices", payload.get("questionCount", 0)),
            ),
        ),
        0,
    )
    progress = _optional_int(payload.get("progress", payload.get("progressPercent")))
    if progress is not None:
        progress = max(0, min(progress, 100))

    cover_image = _first_non_empty(
        payload,
        "coverImage",
        "cover_image",
        "thumbnailUrl",
        "heroImageUrl",
    ) or None

    updated_at = _to_datetime(
        payload.get(
            "updatedAt",
            payload.get("updated_at", payload.get("lastPlayedAt", payload.get("last_played_at"))),
        )
    )
    created_at = _to_datetime_or_none(
        payload.get("createdAt", payload.get("created_at"))
    )
    last_played_at = _to_datetime_or_none(
        payload.get("lastPlayedAt", payload.get("last_played_at"))
    ) or updated_at

    questions_generated = _to_string_list(
        payload.get("questionsGenerated", payload.get("questions_generated", [])),
    )
    theme_title = _first_non_empty(payload, "themeTitle", "title", "storyTitle", "name") or None
    question_count = _optional_int(
        payload.get(
            "questionCount",
            payload.get("question_count", payload.get("choicesAvailable")),
        ),
    )

    return UserStoryRecord(
        story_id=story_id,
        user_id=_first_non_empty(payload, "userId", "user_id", default=user_id),
        session_id=session_id,
        title=title,
        genre=genre,
        character_name=character_name,
        archetype=archetype,
        last_scene_id=last_scene_id,
        updated_at=updated_at,
        choices_available=max(0, choices_available),
        progress=progress,
        cover_image=cover_image,
        last_played_at=last_played_at,
        status=_first_non_empty(payload, "status") or None,
        theme_id=_first_non_empty(payload, "themeId", "theme_id") or None,
        theme_title=theme_title,
        theme_category=_first_non_empty(payload, "themeCategory", "theme_category", "genre") or None,
        theme_description=_first_non_empty(
            payload,
            "themeDescription",
            "theme_description",
            "description",
        )
        or None,
        question_count=question_count,
        questions_generated=questions_generated,
        created_at=created_at,
    )


def _to_datetime(raw: Any) -> datetime:
    value = _to_datetime_or_none(raw)
    return value if value is not None else datetime.now(UTC)


def _to_datetime_or_none(raw: Any) -> datetime | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        if raw.tzinfo is None:
            return raw.replace(tzinfo=UTC)
        return raw.astimezone(UTC)
    if hasattr(raw, "to_datetime"):
        value = raw.to_datetime()
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)
            return value.astimezone(UTC)
        return None
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        normalized = text.replace("Z", "+00:00")
        try:
            value = datetime.fromisoformat(normalized)
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)
            return value.astimezone(UTC)
        except ValueError:
            return None
    return None


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []


def _first_non_empty(payload: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default
