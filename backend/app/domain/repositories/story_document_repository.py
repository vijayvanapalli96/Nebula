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

    def update_scene_choice_media(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
        choice_id: str,
        image_url: str | None = None,
        video_url: str | None = None,
    ) -> None:
        """Update a single choice's imageUrl/videoUrl inside a scene document."""
        ...

    def get_scene(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
    ) -> dict | None:
        """Read one scene document from users/{user_id}/stories/{story_id}/scenes/{scene_id}."""
        ...

    def update_scene_forward_link(
        self,
        user_id: str,
        story_id: str,
        parent_scene_id: str,
        choice_id: str,
        next_scene_id: str,
    ) -> None:
        """Add next_scene_id to parent's nextSceneIds list and set the matching
        choice's nextSceneId field."""
        ...

    def get_story_payload(
        self,
        user_id: str,
        story_id: str,
    ) -> dict[str, list[dict]]:
        """Return story sub-collections as raw documents: questions, answers, scenes."""
        ...
