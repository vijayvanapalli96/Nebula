from __future__ import annotations

from app.domain.models.story import StorySceneRecord
from app.domain.repositories.story_scene_repository import StorySceneRepository


class InMemoryStorySceneRepository(StorySceneRepository):
    def __init__(self, scenes_by_story_id: dict[str, list[StorySceneRecord]] | None = None) -> None:
        self._scenes_by_story_id = scenes_by_story_id or {}

    def list_by_story_id(self, story_id: str) -> list[StorySceneRecord]:
        return list(self._scenes_by_story_id.get(story_id, []))
