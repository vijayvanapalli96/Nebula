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
        # { user_id: { story_id: { question_id: answer_payload } } }
        self._answers: dict[str, dict[str, dict[str, dict]]] = {}
        # { user_id: { story_id: { scene_id: scene_payload } } }
        self._scenes: dict[str, dict[str, dict[str, dict]]] = {}

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

    def save_answers(
        self,
        user_id: str,
        story_id: str,
        answers: list[dict],
        custom_input: str,
    ) -> None:
        answers_map = (
            self._answers
            .setdefault(user_id, {})
            .setdefault(story_id, {})
        )
        for item in answers:
            question_id = str(item.get("questionId", "")).strip() or f"q_{len(answers_map) + 1}"
            answers_map[question_id] = {
                **item,
                "savedAt": datetime.now(UTC),
            }

        story = self._stories.get(user_id, {}).get(story_id)
        if story is not None:
            story.updated_at = datetime.now(UTC)
            if custom_input and hasattr(story, "custom_input"):
                setattr(story, "custom_input", custom_input)

    def store_scene(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
        scene_data: dict,
    ) -> None:
        (
            self._scenes
            .setdefault(user_id, {})
            .setdefault(story_id, {})
        )[scene_id] = {
            **scene_data,
            "sceneId": scene_data.get("sceneId", scene_id),
            "createdAt": scene_data.get("createdAt", datetime.now(UTC)),
        }

    def get_scene(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
    ) -> dict | None:
        return (
            self._scenes
            .get(user_id, {})
            .get(story_id, {})
            .get(scene_id)
        )

    def update_scene_choice_media(
        self,
        user_id: str,
        story_id: str,
        scene_id: str,
        choice_id: str,
        image_url: str | None = None,
        video_url: str | None = None,
    ) -> None:
        scene = self.get_scene(user_id=user_id, story_id=story_id, scene_id=scene_id)
        if scene is None:
            return

        choices = scene.get("choices", [])
        if not isinstance(choices, list):
            return

        for choice in choices:
            if not isinstance(choice, dict):
                continue
            if choice.get("choiceId") != choice_id:
                continue
            if image_url is not None:
                choice["imageUrl"] = image_url
            if video_url is not None:
                choice["videoUrl"] = video_url
            break

        scene["updatedAt"] = datetime.now(UTC)

    def get_story_payload(
        self,
        user_id: str,
        story_id: str,
    ) -> dict[str, list[dict]]:
        question_docs = []
        for question_id, question in (
            self._questions.get(user_id, {}).get(story_id, {}).items()
        ):
            question_docs.append(
                {
                    "questionId": question_id,
                    "question": question.question,
                    "options": [
                        {
                            "text": option.text,
                            "imagePrompt": option.image_prompt,
                            "imageUrl": option.image_url,
                        }
                        for option in question.options
                    ],
                    "createdAt": question.created_at,
                }
            )

        answer_docs = list(
            self._answers.get(user_id, {}).get(story_id, {}).values()
        )
        scene_docs = list(
            self._scenes.get(user_id, {}).get(story_id, {}).values()
        )

        return {
            "questions": question_docs,
            "answers": answer_docs,
            "scenes": scene_docs,
        }
