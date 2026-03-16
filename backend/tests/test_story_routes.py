from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.application.dto.story_results import (
    OpeningSceneResult,
    QuestionsResult,
    StoryActionResult,
    StoryCardView,
    StoryDetailView,
    StorySceneAssetRefsView,
    StorySceneGenerationStatusView,
    StorySceneLocationView,
    StorySceneView,
    StoryStartResult,
    StoryThemeView,
)
from app.application.errors import SessionNotFoundError
from app.domain.models.story import InitialQuestion, OpeningChoice, OpeningScene, QuestionOption, Scene, SceneChoice, SceneMetadata
from app.main import create_app
from app.presentation.api.dependencies import get_use_case, require_auth


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
    def __init__(self) -> None:
        self.last_user_id: str | None = None
        self.last_story_detail_request: tuple[str, str] | None = None

    async def generate_questions(self, command):  # noqa: ANN001
        return QuestionsResult(
            theme=command.theme,
            questions=[
                InitialQuestion(
                    question="What color is the sky?",
                    options=[
                        QuestionOption(text="Red", image_prompt="red sky", image_uri="https://storage.googleapis.com/red-sky.png"),
                        QuestionOption(text="Blue", image_prompt="blue sky", image_uri="https://storage.googleapis.com/blue-sky.png"),
                        QuestionOption(text="Green", image_prompt="green sky", image_uri="https://storage.googleapis.com/green-sky.png"),
                        QuestionOption(text="Black", image_prompt="black sky", image_uri="https://storage.googleapis.com/black-sky.png"),
                    ],
                ),
                InitialQuestion(
                    question="What drives the hero?",
                    options=[
                        QuestionOption(text="Revenge", image_prompt="fire fist", image_uri="https://storage.googleapis.com/fire-fist.png"),
                        QuestionOption(text="Curiosity", image_prompt="glowing book", image_uri="https://storage.googleapis.com/glowing-book.png"),
                        QuestionOption(text="Love", image_prompt="two hearts", image_uri="https://storage.googleapis.com/two-hearts.png"),
                        QuestionOption(text="Duty", image_prompt="knight kneeling", image_uri="https://storage.googleapis.com/knight-kneeling.png"),
                    ],
                ),
                InitialQuestion(
                    question="What lurks in the shadows?",
                    options=[
                        QuestionOption(text="Ghosts", image_prompt="ghosts", image_uri="https://storage.googleapis.com/ghosts.png"),
                        QuestionOption(text="Machines", image_prompt="machines", image_uri="https://storage.googleapis.com/machines.png"),
                        QuestionOption(text="Beasts", image_prompt="beasts", image_uri="https://storage.googleapis.com/beasts.png"),
                        QuestionOption(text="Nothing", image_prompt="void", image_uri="https://storage.googleapis.com/void.png"),
                    ],
                ),
                InitialQuestion(
                    question="How does the story end?",
                    options=[
                        QuestionOption(text="In flames", image_prompt="flames", image_uri="https://storage.googleapis.com/flames.png"),
                        QuestionOption(text="With a whisper", image_prompt="mist", image_uri="https://storage.googleapis.com/mist.png"),
                        QuestionOption(text="With a dance", image_prompt="dance", image_uri="https://storage.googleapis.com/dance.png"),
                        QuestionOption(text="Silently", image_prompt="silence", image_uri="https://storage.googleapis.com/silence.png"),
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
                    ),
                    OpeningChoice(
                        choice_id="B",
                        choice_text="Climb the tower",
                        direction_hint="A broader view",
                        image_prompt="tall tower clouds",
                        video_prompt="camera tilts up tower",
                    ),
                    OpeningChoice(
                        choice_id="C",
                        choice_text="Follow the stranger",
                        direction_hint="Mystery deepens",
                        image_prompt="cloaked figure corner",
                        video_prompt="camera follows figure",
                    ),
                ],
            ),
        )

    def fire_opening_scene_media(self, scene):  # noqa: ANN001
        return None

    async def start_story(self, command):  # noqa: ANN001
        return StoryStartResult(session_id="session-1", scene=_scene(scene_id="scene-1", chapter=1))

    async def apply_action(self, command):  # noqa: ANN001
        if command.session_id == "missing":
            raise SessionNotFoundError("Session 'missing' not found.")
        return StoryActionResult(session_id=command.session_id, scene=_scene("scene-2", 2))

    def list_active_stories(self, user_id: str) -> list[StoryCardView]:
        self.last_user_id = user_id
        return [
            StoryCardView(
                story_id="story-1",
                session_id="session-1",
                title="Mara Vale: Noir Arc",
                genre="Noir",
                character_name="Mara Vale",
                archetype="Reluctant Detective",
                last_scene_id="scene-2",
                updated_at=datetime.now(UTC),
                choices_available=3,
                progress=45,
                cover_image="https://example.com/story-cover.png",
                status="active",
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

    def list_story_scenes(self, story_id: str) -> list[StorySceneView]:
        return [
            StorySceneView(
                scene_id="scene_001",
                story_id=story_id,
                chapter_number=1,
                scene_number=1,
                title="Crimson Echoes",
                description="The neon-soaked city pulses beneath you.",
                short_summary="Kira overlooks the city and spots three possible paths.",
                full_narrative="The city hums with danger below the rooftop edge.",
                parent_scene_id=None,
                selected_choice_id_from_parent=None,
                path_depth=0,
                is_root=True,
                is_current_checkpoint=True,
                is_ending=False,
                ending_type=None,
                scene_type="opening",
                mood="dark",
                location=StorySceneLocationView(
                    name="Skyline Rooftop",
                    location_type="city_rooftop",
                ),
                characters_present=["kira_voss"],
                asset_refs=StorySceneAssetRefsView(
                    hero_image_id="asset_hero_001",
                    scene_image_id="asset_scene_001",
                    scene_video_id="asset_video_001",
                    scene_audio_id=None,
                ),
                generation_status=StorySceneGenerationStatusView(
                    text="completed",
                    image="completed",
                    video="completed",
                ),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

    def get_story_detail(self, user_id: str, story_id: str) -> StoryDetailView | None:
        self.last_story_detail_request = (user_id, story_id)
        if story_id == "missing":
            return None
        return StoryDetailView(
            story_id=story_id,
            user_id=user_id,
            session_id=story_id,
            title="The Last Detective",
            genre="crime",
            character_name="Kira Voss",
            archetype="Investigator",
            last_scene_id="scene_010",
            updated_at=datetime.now(UTC),
            choices_available=4,
            progress=65,
            cover_image="https://example.com/last-detective.png",
            last_played_at=datetime.now(UTC),
            status="questions_generated",
            theme_id="theme-crime",
            theme_title="The Last Detective",
            theme_category="crime",
            theme_description="A neon mystery unfolds in the rain.",
            question_count=4,
            questions_generated=[
                "What drives the hero?",
                "Who can be trusted?",
            ],
            created_at=datetime.now(UTC),
        )


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    fake_use_case = FakeUseCase()
    app.dependency_overrides[get_use_case] = lambda: fake_use_case
    app.dependency_overrides[require_auth] = lambda: "test-user"
    with TestClient(app) as test_client:
        test_client.app.state.fake_use_case = fake_use_case
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
    assert body[0]["story_id"] == "story-1"
    assert body[0]["session_id"] == "session-1"
    assert body[0]["choices_available"] == 3
    assert body[0]["progress"] == 45
    assert body[0]["cover_image"] == "https://example.com/story-cover.png"
    assert body[0]["status"] == "active"
    assert client.app.state.fake_use_case.last_user_id == "test-user"


def test_list_story_themes_route_returns_themes(client: TestClient) -> None:
    response = client.get("/story/themes")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "genre-noir"
    assert body[0]["title"] == "Noir Detective"


def test_list_story_scenes_route_returns_scenes(client: TestClient) -> None:
    response = client.get("/stories/story_123/scenes")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["scene_id"] == "scene_001"
    assert body[0]["story_id"] == "story_123"
    assert body[0]["location"]["name"] == "Skyline Rooftop"


def test_story_detail_route_returns_full_story_payload(client: TestClient) -> None:
    response = client.get("/story/test-user/story-1")
    assert response.status_code == 200
    body = response.json()
    assert body["story_id"] == "story-1"
    assert body["user_id"] == "test-user"
    assert body["title"] == "The Last Detective"
    assert body["theme_id"] == "theme-crime"
    assert body["theme_description"]
    assert body["question_count"] == 4
    assert len(body["questions_generated"]) == 2
    assert client.app.state.fake_use_case.last_story_detail_request == ("test-user", "story-1")


def test_story_detail_route_rejects_uid_mismatch(client: TestClient) -> None:
    client.app.dependency_overrides[require_auth] = lambda: "another-user"
    response = client.get("/story/test-user/story-1")
    assert response.status_code == 403
    assert "does not match" in response.json()["detail"].lower()
    client.app.dependency_overrides[require_auth] = lambda: "test-user"


def test_story_detail_route_returns_404_when_story_missing(client: TestClient) -> None:
    response = client.get("/story/test-user/missing")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_generate_questions_route_returns_questions(client: TestClient) -> None:
    response = client.post(
        "/story/questions",
        json={"theme": "Cyberpunk Noir"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["theme"] == "Cyberpunk Noir"
    assert "media_request_id" not in body
    assert len(body["questions"]) == 4
    for q in body["questions"]:
        assert "question" in q
        assert len(q["options"]) == 4
        for opt in q["options"]:
            assert "text" in opt
            assert "image_prompt" in opt
            assert "image_uri" in opt
            assert opt["image_uri"] is not None
            assert opt["image_uri"].startswith("https://")


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
    assert body["choices"][0]["image_prompt"] == "dark alley neon"
    assert body["choices"][0]["video_prompt"] == "camera pushes into alley"


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
