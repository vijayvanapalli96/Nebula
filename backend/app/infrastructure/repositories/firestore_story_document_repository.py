"""Firestore-backed StoryDocumentRepository.

Persists story documents and their question sub-collections under the path:
    users/{user_id}/stories/{story_id}
    users/{user_id}/stories/{story_id}/questions/{question_id}
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.models.story_document import StoredQuestion, StoryDocument
from app.domain.repositories.story_document_repository import StoryDocumentRepository


class FirestoreStoryDocumentRepository:
    """Write story documents and questions to Firestore."""

    def __init__(self, firestore_client: Any) -> None:
        self._db = firestore_client

    # ── StoryDocumentRepository protocol ─────────────────────────────────────

    def create(self, doc: StoryDocument) -> None:
        ref = (
            self._db.collection("users")
            .document(doc.user_id)
            .collection("stories")
            .document(doc.story_id)
        )
        ref.set(
            {
                "storyId": doc.story_id,
                "userId": doc.user_id,
                "themeId": doc.theme_id,
                "themeTitle": doc.theme_title,
                "themeCategory": doc.theme_category,
                "themeDescription": doc.theme_description,
                "status": doc.status,
                "createdAt": doc.created_at,
                "updatedAt": doc.updated_at,
            }
        )

    def update_status(
        self,
        user_id: str,
        story_id: str,
        status: str,
        summary: dict,  # noqa: ANN001
    ) -> None:
        ref = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
        )
        ref.update(
            {
                "status": status,
                "updatedAt": datetime.now(UTC),
                **summary,
            }
        )

    def store_question(
        self,
        user_id: str,
        story_id: str,
        question: StoredQuestion,
    ) -> None:
        ref = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
            .collection("questions")
            .document(question.question_id)
        )
        ref.set(
            {
                "questionId": question.question_id,
                "question": question.question,
                "options": [
                    {
                        "text": opt.text,
                        "imagePrompt": opt.image_prompt,
                        "imageUrl": opt.image_url,
                        "gcsPath": opt.gcs_path,
                    }
                    for opt in question.options
                ],
                "createdAt": question.created_at,
            }
        )
