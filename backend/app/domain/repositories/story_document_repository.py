"""Port protocol for persisting story documents and their sub-collections."""
from __future__ import annotations

from typing import Protocol

from app.domain.models.story_document import StoredQuestion, StoryDocument


class StoryDocumentRepository(Protocol):
    def create(self, doc: StoryDocument) -> None:
        """Persist a new story document under users/{user_id}/stories/{story_id}."""
        ...

    def update_status(
        self,
        user_id: str,
        story_id: str,
        status: str,
        summary: dict,  # noqa: ANN401
    ) -> None:
        """Update the story status field and merge any extra summary fields."""
        ...

    def store_question(
        self,
        user_id: str,
        story_id: str,
        question: StoredQuestion,
    ) -> None:
        """Write a question document to users/{user_id}/stories/{story_id}/questions/{question_id}."""
        ...

    def save_answers(
        self,
        user_id: str,
        story_id: str,
        answers: list[dict],
        custom_input: str,
    ) -> None:
        """Persist questionnaire answers to users/{user_id}/stories/{story_id}/answers/."""
        ...

    def store_scene(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
        scene_data: dict,
    ) -> None:
        """Write a scene document to users/{user_id}/stories/{story_id}/scenes/{scene_id}."""
        ...
