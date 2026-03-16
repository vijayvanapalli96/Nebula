"""Use case: create the initial story document in Firestore."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.models.story_document import StoryDocument
from app.domain.models.theme_detail import ThemeDetail
from app.domain.repositories.story_document_repository import StoryDocumentRepository


class CreateStoryUseCase:
    def __init__(self, repository: StoryDocumentRepository) -> None:
        self._repository = repository

    def execute(self, user_id: str, theme: ThemeDetail) -> str:
        """Create a new story document and return the generated story_id."""
        story_id = str(uuid4())
        now = datetime.now(UTC)
        doc = StoryDocument(
            story_id=story_id,
            user_id=user_id,
            theme_id=theme.theme_id,
            theme_title=theme.title,
            theme_category=theme.category,
            theme_description=theme.description,
            theme_image_url=theme.image_url,
            status="initializing",
            created_at=now,
            updated_at=now,
        )
        self._repository.create(doc)
        return story_id
