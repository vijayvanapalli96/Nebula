"""In-memory StoryDocumentRepository for local development / tests."""
from __future__ import annotations

from datetime import UTC, datetime

from app.domain.models.story_document import StoredQuestion, StoryDocument
from app.domain.repositories.story_document_repository import StoryDocumentRepository


class InMemoryStoryDocumentRepository:
    """Thread-unsafe in-memory store; suitable for single-process dev/testing."""

    def __init__(self) -> None:
        # { user_id: { story_id: StoryDocument } }
        self._stories: dict[str, dict[str, StoryDocument]] = {}
        # { user_id: { story_id: { question_id: StoredQuestion } } }
        self._questions: dict[str, dict[str, dict[str, StoredQuestion]]] = {}

    def create(self, doc: StoryDocument) -> None:
        self._stories.setdefault(doc.user_id, {})[doc.story_id] = doc

    def update_status(
        self,
        user_id: str,
        story_id: str,
        status: str,
        summary: dict,  # noqa: ANN001
    ) -> None:
        story = self._stories.get(user_id, {}).get(story_id)
        if story is None:
            return
        story.status = status
        story.updated_at = datetime.now(UTC)
        for key, value in summary.items():
            if hasattr(story, key):
                object.__setattr__(story, key, value)

    def store_question(
        self,
        user_id: str,
        story_id: str,
        question: StoredQuestion,
    ) -> None:
        (
            self._questions
            .setdefault(user_id, {})
            .setdefault(story_id, {})
        )[question.question_id] = question
