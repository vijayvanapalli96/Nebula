from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.application.dto.story_results import StoryActionResult, StoryCardView, StoryStartResult
from app.application.errors import SessionNotFoundError
from app.domain.models.story import Scene, SceneChoice, SceneMetadata
from app.main import create_app
from app.presentation.api.dependencies import get_use_case


def _scene(scene_id: str, chapter: int) -> Scene:
    return Scene(
        metadata=SceneMetadata(
            scene_id=scene_id,
            chapter=chapter,
            mood="tense",
            tension=min(chapter * 20, 100),
        ),
        visual_prompt="rainy alleyway, cinematic",
        narrative_text="A short cinematic beat with escalating stakes.",
        choices=[
            SceneChoice(choice_id="A", label="Press forward", consequence_hint="Bold move"),
            SceneChoice(choice_id="B", label="Hold position", consequence_hint="Safer"),
            SceneChoice(choice_id="C", label="Retreat", consequence_hint="Lose momentum"),
        ],
    )


class FakeUseCase:
    async def start_story(self, command):  # noqa: ANN001
        return StoryStartResult(session_id="session-1", scene=_scene(scene_id="scene-1", chapter=1))

    async def apply_action(self, command):  # noqa: ANN001
        if command.session_id == "missing":
            raise SessionNotFoundError("Session 'missing' not found.")
        return StoryActionResult(session_id=command.session_id, scene=_scene("scene-2", 2))

    def list_active_stories(self) -> list[StoryCardView]:
        return [
            StoryCardView(
                session_id="session-1",
                title="Mara Vale: Noir Arc",
                genre="Noir",
                character_name="Mara Vale",
                archetype="Reluctant Detective",
                last_scene_id="scene-2",
                updated_at=datetime.now(UTC),
                choices_available=3,
            )
        ]


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_use_case] = lambda: FakeUseCase()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_start_story_route_returns_scene_payload(client: TestClient) -> None:
    response = client.post(
        "/story/start",
        json={
            "genre": "Noir",
            "name": "Mara Vale",
            "archetype": "Reluctant Detective",
            "motivation": "Find her missing brother",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["session_id"] == "session-1"
    assert body["scene"]["metadata"]["scene_id"] == "scene-1"
    assert len(body["scene"]["choices"]) == 3


def test_story_action_route_returns_404_for_missing_session(client: TestClient) -> None:
    response = client.post(
        "/story/action",
        json={
            "session_id": "missing",
            "choice_id": "A",
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_stories_route_returns_cards(client: TestClient) -> None:
    response = client.get("/stories/me")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["session_id"] == "session-1"
    assert body[0]["choices_available"] == 3

