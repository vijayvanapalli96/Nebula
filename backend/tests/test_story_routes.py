from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.application.dto.story_results import OpeningSceneResult, QuestionsResult, StoryActionResult, StoryCardView, StoryStartResult, StoryThemeView
from app.application.errors import SessionNotFoundError
from app.domain.models.story import InitialQuestion, OpeningChoice, OpeningScene, QuestionOption, Scene, SceneChoice, SceneMetadata
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
    async def generate_questions(self, command):  # noqa: ANN001
        return QuestionsResult(
            theme=command.theme,
            questions=[
                InitialQuestion(
                    question="What color is the sky?",
                    options=[
                        QuestionOption(text="Red", image_prompt="red sky"),
                        QuestionOption(text="Blue", image_prompt="blue sky"),
                        QuestionOption(text="Green", image_prompt="green sky"),
                        QuestionOption(text="Black", image_prompt="black sky"),
                    ],
                ),
                InitialQuestion(
                    question="What drives the hero?",
                    options=[
                        QuestionOption(text="Revenge", image_prompt="fire fist"),
                        QuestionOption(text="Curiosity", image_prompt="glowing book"),
                        QuestionOption(text="Love", image_prompt="two hearts"),
                        QuestionOption(text="Duty", image_prompt="knight kneeling"),
                    ],
                ),
                InitialQuestion(
                    question="What lurks in the shadows?",
                    options=[
                        QuestionOption(text="Ghosts", image_prompt="ghosts"),
                        QuestionOption(text="Machines", image_prompt="machines"),
                        QuestionOption(text="Beasts", image_prompt="beasts"),
                        QuestionOption(text="Nothing", image_prompt="void"),
                    ],
                ),
                InitialQuestion(
                    question="How does the story end?",
                    options=[
                        QuestionOption(text="In flames", image_prompt="flames"),
                        QuestionOption(text="With a whisper", image_prompt="mist"),
                        QuestionOption(text="With a dance", image_prompt="dance"),
                        QuestionOption(text="Silently", image_prompt="silence"),
                    ],
                ),
            ],
        )

    async def generate_opening_scene(self, command):  # noqa: ANN001
        return OpeningSceneResult(
            theme=command.theme,
            character_name=command.character_name,
            scene=OpeningScene(
                scene_title="Crimson Echoes",
                scene_description="The neon-soaked city pulses with hidden danger.",
                video_prompt="Sweeping aerial shot of a neon-drenched cyberpunk city at dusk",
                choices=[
                    OpeningChoice(
                        choice_id="A",
                        choice_text="Enter the alley",
                        direction_hint="Danger awaits",
                        image_prompt="dark alley neon",
                        video_prompt="camera pushes into alley",
                        image_uri="https://storage.example.com/choice-a.png",
                        video_uri="https://storage.example.com/choice-a.mp4",
                    ),
                    OpeningChoice(
                        choice_id="B",
                        choice_text="Climb the tower",
                        direction_hint="A broader view",
                        image_prompt="tall tower clouds",
                        video_prompt="camera tilts up tower",
                        image_uri="https://storage.example.com/choice-b.png",
                        video_uri="https://storage.example.com/choice-b.mp4",
                    ),
                    OpeningChoice(
                        choice_id="C",
                        choice_text="Follow the stranger",
                        direction_hint="Mystery deepens",
                        image_prompt="cloaked figure corner",
                        video_prompt="camera follows figure",
                        image_uri="https://storage.example.com/choice-c.png",
                        video_uri="https://storage.example.com/choice-c.mp4",
                    ),
                ],
            ),
        )

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

    def list_story_themes(self) -> list[StoryThemeView]:
        return [
            StoryThemeView(
                id="genre-noir",
                title="Noir Detective",
                tagline="Solve a crime in a rain-soaked city.",
                description="Secrets hide in every shadow.",
                image="https://example.com/noir.jpg",
                accent_color="rgba(234,179,8,0.6)",
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


def test_list_story_themes_route_returns_themes(client: TestClient) -> None:
    response = client.get("/story/themes")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "genre-noir"
    assert body[0]["title"] == "Noir Detective"


def test_generate_questions_route_returns_questions(client: TestClient) -> None:
    response = client.post(
        "/story/questions",
        json={"theme": "Cyberpunk Noir"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["theme"] == "Cyberpunk Noir"
    assert len(body["questions"]) == 4
    for q in body["questions"]:
        assert "question" in q
        assert len(q["options"]) == 4
        for opt in q["options"]:
            assert "text" in opt
            assert "image_uri" in opt


def test_generate_questions_route_rejects_empty_theme(client: TestClient) -> None:
    response = client.post(
        "/story/questions",
        json={"theme": ""},
    )
    assert response.status_code == 422


def test_opening_scene_route_returns_scene(client: TestClient) -> None:
    response = client.post(
        "/story/opening",
        json={
            "theme": "Cyberpunk Noir",
            "character_name": "Kira Voss",
            "answers": [
                {"question": "What color is the sky?", "answer": "Crimson"},
                {"question": "What drives the hero?", "answer": "Revenge"},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["theme"] == "Cyberpunk Noir"
    assert body["character_name"] == "Kira Voss"
    assert body["scene_title"] == "Crimson Echoes"
    assert len(body["choices"]) == 3
    assert body["choices"][0]["choice_id"] == "A"
    assert body["choices"][0]["image_uri"] == "https://storage.example.com/choice-a.png"
    assert body["choices"][0]["video_uri"] == "https://storage.example.com/choice-a.mp4"


def test_opening_scene_route_rejects_missing_answers(client: TestClient) -> None:
    response = client.post(
        "/story/opening",
        json={
            "theme": "Cyberpunk Noir",
            "character_name": "Kira Voss",
            "answers": [],
        },
    )
    assert response.status_code == 422
