from __future__ import annotations

from typing import Protocol

from app.domain.models.story import UserStoryRecord


class UserStoryRepository(Protocol):
    def list_by_user_id(self, user_id: str) -> list[UserStoryRecord]:
        ...

    def get_by_user_id_and_story_id(
        self,
        user_id: str,
        story_id: str,
    ) -> UserStoryRecord | None:
        ...
