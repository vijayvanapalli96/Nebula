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
                "themeImageUrl": doc.theme_image_url,
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
        ref.set(
            {
                "status": status,
                "updatedAt": datetime.now(UTC),
                **summary,
            },
            merge=True,
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

    def save_answers(
        self,
        user_id: str,
        story_id: str,
        answers: list[dict],
        custom_input: str,
    ) -> None:
        """Persist each answer as its own document; store customInput on the story doc."""
        story_ref = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
        )
        answers_col = story_ref.collection("answers")
        for ans in answers:
            answers_col.document(ans["questionId"]).set({
                **ans,
                "savedAt": datetime.now(UTC),
            })
        story_ref.update({
            "customInput": custom_input,
            "updatedAt": datetime.now(UTC),
        })

    def store_scene(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
        scene_data: dict,
    ) -> None:
        """Write scene_data to users/{user_id}/stories/{story_id}/scenes/{scene_id}."""
        (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
            .collection("scenes")
            .document(scene_id)
            .set({
                **scene_data,
                "createdAt": datetime.now(UTC),
            })
        )

    def get_scene(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
    ) -> dict | None:
        """Read a scene document. Returns the raw dict or None if not found."""
        snap = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
            .collection("scenes")
            .document(scene_id)
            .get()
        )
        if not snap.exists:
            return None
        return snap.to_dict() or {}

    def get_story_payload(
        self,
        user_id: str,
        story_id: str,
    ) -> dict[str, list[dict]]:
        """Read questions, answers, and scenes subcollections for one story."""
        story_ref = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
        )

        def _read_subcollection(name: str, id_key: str) -> list[dict]:
            docs = story_ref.collection(name).stream()
            rows: list[dict] = []
            for doc in docs:
                payload = doc.to_dict() or {}
                payload.setdefault(id_key, doc.id)
                rows.append(payload)
            return rows

        return {
            "questions": _read_subcollection("questions", "questionId"),
            "answers": _read_subcollection("answers", "questionId"),
            "scenes": _read_subcollection("scenes", "sceneId"),
        }

    def update_scene_choice_media(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
        choice_id: str,
        image_url: str | None = None,
        video_url: str | None = None,
    ) -> None:
        """Read-modify-write the choices array to set imageUrl/videoUrl on one choice.

        Safe within asyncio: sync Firestore calls do not yield to the event loop,
        so concurrent tasks for different choice_ids cannot interleave here.
        """
        ref = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
            .collection("scenes")
            .document(scene_id)
        )
        snap = ref.get()
        if not snap.exists:
            return
        data = snap.to_dict() or {}
        choices = list(data.get("choices", []))
        for choice in choices:
            if choice.get("choiceId") == choice_id:
                if image_url is not None:
                    choice["imageUrl"] = image_url
                if video_url is not None:
                    choice["videoUrl"] = video_url
                break
        ref.update({"choices": choices, "updatedAt": datetime.now(UTC)})

    def get_scene(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
    ) -> dict | None:
        """Read a scene document from users/{uid}/stories/{storyId}/scenes/{sceneId}."""
        snap = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
            .collection("scenes")
            .document(scene_id)
            .get()
        )
        if not snap.exists:
            return None
        return snap.to_dict()

    def update_scene_forward_link(
        self,
        user_id: str,
        story_id: str,
        parent_scene_id: str,
        choice_id: str,
        next_scene_id: str,
    ) -> None:
        """Add next_scene_id to parent's nextSceneIds and set on the matching choice."""
        ref = (
            self._db.collection("users")
            .document(user_id)
            .collection("stories")
            .document(story_id)
            .collection("scenes")
            .document(parent_scene_id)
        )
        snap = ref.get()
        if not snap.exists:
            return
        data = snap.to_dict() or {}

        # Update nextSceneIds list
        next_ids = list(data.get("nextSceneIds", []))
        if next_scene_id not in next_ids:
            next_ids.append(next_scene_id)

        # Update the matching choice's nextSceneId
        choices = list(data.get("choices", []))
        for choice in choices:
            if choice.get("choiceId") == choice_id:
                choice["nextSceneId"] = next_scene_id
                break

        ref.update({
            "nextSceneIds": next_ids,
            "choices": choices,
            "updatedAt": datetime.now(UTC),
        })
