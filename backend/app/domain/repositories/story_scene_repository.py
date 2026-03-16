from __future__ import annotations

from typing import Protocol

from app.domain.models.story import StorySceneRecord


class StorySceneRepository(Protocol):
    def list_by_story_id(self, story_id: str) -> list[StorySceneRecord]:
        ...
