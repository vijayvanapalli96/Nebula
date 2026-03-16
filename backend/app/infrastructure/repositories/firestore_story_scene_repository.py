from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.models.story import (
    StorySceneAssetRefs,
    StorySceneGenerationStatus,
    StorySceneLocation,
    StorySceneRecord,
)
from app.domain.repositories.story_scene_repository import StorySceneRepository


class FirestoreStorySceneRepository(StorySceneRepository):
    """
    Firestore-backed story scenes repository.
    Expected path: /{stories_collection}/{story_id}/{scenes_subcollection}/{scene_id}
    """

    def __init__(
        self,
        firestore_client: Any,
        stories_collection: str,
        scenes_subcollection: str,
    ) -> None:
        self._client = firestore_client
        self._stories_collection = stories_collection
        self._scenes_subcollection = scenes_subcollection

    def list_by_story_id(self, story_id: str) -> list[StorySceneRecord]:
        docs = (
            self._client.collection(self._stories_collection)
            .document(story_id)
            .collection(self._scenes_subcollection)
            .stream()
        )
        scenes: list[StorySceneRecord] = []
        for doc in docs:
            payload = doc.to_dict() or {}
            scene = _to_scene_record(story_id=story_id, document_id=doc.id, payload=payload)
            if scene is not None:
                scenes.append(scene)
        return sorted(
            scenes,
            key=lambda item: (
                item.chapter_number,
                item.scene_number,
                item.path_depth,
                item.created_at,
            ),
        )


def _to_scene_record(
    story_id: str,
    document_id: str,
    payload: dict[str, Any],
) -> StorySceneRecord | None:
    scene_id = _first_non_empty(payload, "sceneId", "scene_id", default=document_id)
    title = _first_non_empty(payload, "title")
    description = _first_non_empty(payload, "description", "shortSummary")

    if not scene_id or not title or not description:
        return None

    chapter_number = _to_int(payload.get("chapterNumber", payload.get("chapter_number", 1)), 1)
    scene_number = _to_int(payload.get("sceneNumber", payload.get("scene_number", 1)), 1)
    path_depth = _to_int(payload.get("pathDepth", payload.get("path_depth", 0)), 0)

    short_summary = _first_non_empty(
        payload,
        "shortSummary",
        "short_summary",
        default=description,
    )
    full_narrative = _first_non_empty(
        payload,
        "fullNarrative",
        "full_narrative",
        default=description,
    )

    location_payload = payload.get("location")
    location = _to_location(location_payload)

    asset_refs = _to_asset_refs(payload.get("assetRefs"))
    generation_status = _to_generation_status(payload.get("generationStatus"))

    created_at = _to_datetime(payload.get("createdAt", payload.get("created_at")))
    updated_at = _to_datetime(payload.get("updatedAt", payload.get("updated_at")))

    return StorySceneRecord(
        scene_id=scene_id,
        story_id=_first_non_empty(payload, "storyId", "story_id", default=story_id),
        chapter_number=chapter_number,
        scene_number=scene_number,
        title=title,
        description=description,
        short_summary=short_summary,
        full_narrative=full_narrative,
        parent_scene_id=_first_non_empty(payload, "parentSceneId", "parent_scene_id") or None,
        selected_choice_id_from_parent=_first_non_empty(
            payload,
            "selectedChoiceIdFromParent",
            "selected_choice_id_from_parent",
        )
        or None,
        path_depth=path_depth,
        is_root=_to_bool(payload.get("isRoot", payload.get("is_root", False))),
        is_current_checkpoint=_to_bool(
            payload.get("isCurrentCheckpoint", payload.get("is_current_checkpoint", False)),
        ),
        is_ending=_to_bool(payload.get("isEnding", payload.get("is_ending", False))),
        ending_type=_first_non_empty(payload, "endingType", "ending_type") or None,
        scene_type=_first_non_empty(
            payload,
            "sceneType",
            "scene_type",
            default="exploration",
        ),
        mood=_first_non_empty(payload, "mood", default="neutral"),
        location=location,
        characters_present=_to_string_list(
            payload.get("charactersPresent", payload.get("characters_present", [])),
        ),
        asset_refs=asset_refs,
        generation_status=generation_status,
        created_at=created_at,
        updated_at=updated_at,
    )


def _to_location(payload: Any) -> StorySceneLocation | None:
    if not isinstance(payload, dict):
        return None
    name = _first_non_empty(payload, "name")
    location_type = _first_non_empty(payload, "type", "location_type")
    if not name and not location_type:
        return None
    return StorySceneLocation(name=name or "Unknown", location_type=location_type or "unknown")


def _to_asset_refs(payload: Any) -> StorySceneAssetRefs:
    if not isinstance(payload, dict):
        return StorySceneAssetRefs()
    return StorySceneAssetRefs(
        hero_image_id=_first_non_empty(payload, "heroImageId", "hero_image_id") or None,
        scene_image_id=_first_non_empty(payload, "sceneImageId", "scene_image_id") or None,
        scene_video_id=_first_non_empty(payload, "sceneVideoId", "scene_video_id") or None,
        scene_audio_id=_first_non_empty(payload, "sceneAudioId", "scene_audio_id") or None,
    )


def _to_generation_status(payload: Any) -> StorySceneGenerationStatus:
    if not isinstance(payload, dict):
        return StorySceneGenerationStatus()
    return StorySceneGenerationStatus(
        text=_first_non_empty(payload, "text", default="pending"),
        image=_first_non_empty(payload, "image", default="pending"),
        video=_first_non_empty(payload, "video", default="pending"),
    )


def _to_datetime(raw: Any) -> datetime:
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
    return datetime.now(UTC)


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _to_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            output.append(text)
    return output


def _first_non_empty(payload: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default
