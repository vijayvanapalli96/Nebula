from __future__ import annotations

import asyncio

import pytest

from app.application.dto.story_commands import ApplyActionCommand, GenerateOpeningSceneCommand, GenerateQuestionsCommand, QuestionAnswer, StartStoryCommand
from app.application.errors import InvalidChoiceError
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.domain.models.story import (
    InitialQuestion,
    OpeningChoice,
    OpeningScene,
    QuestionOption,
    Scene,
    SceneChoice,
    SceneMetadata,
    StorySceneAssetRefs,
    StorySceneGenerationStatus,
    StorySceneLocation,
    StorySceneRecord,
    StoryTheme,
    UserStoryRecord,
    utc_now,
)
from app.infrastructure.repositories.in_memory_story_repository import InMemoryStoryStateRepository


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


class FakeGenerator:
    async def generate_initial_questions(self, theme):  # noqa: ANN001
        return [
            InitialQuestion(
                question="What color is the sky in your world?",
                options=[
                    QuestionOption(text="Crimson", image_prompt="A blood-red sky over a desolate landscape"),
                    QuestionOption(text="Silver", image_prompt="A shimmering silver sky with metallic clouds"),
                    QuestionOption(text="Emerald", image_prompt="A lush green sky above a mystical forest"),
                    QuestionOption(text="Obsidian", image_prompt="A pitch-black sky with faint glowing stars"),
                ],
            ),
            InitialQuestion(
                question="What drives the hero?",
                options=[
                    QuestionOption(text="Revenge", image_prompt="A clenched fist surrounded by flames"),
                    QuestionOption(text="Curiosity", image_prompt="An open ancient book glowing with light"),
                    QuestionOption(text="Love", image_prompt="Two silhouettes reaching for each other"),
                    QuestionOption(text="Duty", image_prompt="A knight kneeling before a throne"),
                ],
            ),
            InitialQuestion(
                question="What lurks in the shadows?",
                options=[
                    QuestionOption(text="Ghosts", image_prompt="Translucent spirits floating in darkness"),
                    QuestionOption(text="Machines", image_prompt="Mechanical eyes glowing in shadowy corridors"),
                    QuestionOption(text="Beasts", image_prompt="Glowing predatory eyes in a dark forest"),
                    QuestionOption(text="Nothing", image_prompt="Empty dark void stretching infinitely"),
                ],
            ),
            InitialQuestion(
                question="How does the story end?",
                options=[
                    QuestionOption(text="In flames", image_prompt="A city engulfed in towering flames"),
                    QuestionOption(text="With a whisper", image_prompt="A lone figure fading into mist"),
                    QuestionOption(text="With a dance", image_prompt="Silhouettes dancing under moonlight"),
                    QuestionOption(text="With silence", image_prompt="An empty room with dust motes floating"),
                ],
            ),
        ]

    async def generate_option_image(self, prompt):  # noqa: ANN001
        return b"fake-png-bytes"

    async def generate_opening_scene(self, state):  # noqa: ANN001
        return _scene(scene_id="scene-1", chapter=1)

    async def generate_opening_scene_from_answers(
        self, theme, character_name, answers  # noqa: ANN001
    ):
        return OpeningScene(
            scene_title="Crimson Echoes",
            scene_description="The neon-soaked city pulses beneath you.",
            video_prompt="Aerial drone shot descending into a neon-lit cyberpunk city at night",
            choices=[
                OpeningChoice(
                    choice_id="A",
                    choice_text="Enter the alley",
                    direction_hint="Danger awaits",
                    image_prompt="A dark alley with neon signs flickering",
                    video_prompt="Camera pushes into a narrow alley as shadows shift",
                ),
                OpeningChoice(
                    choice_id="B",
                    choice_text="Climb the tower",
                    direction_hint="A broader view",
                    image_prompt="A towering skyscraper reaching into clouds",
                    video_prompt="Camera tilts upward along a massive glass tower",
                ),
                OpeningChoice(
                    choice_id="C",
                    choice_text="Follow the stranger",
                    direction_hint="Mystery deepens",
                    image_prompt="A mysterious cloaked figure disappearing around a corner",
                    video_prompt="Camera follows a shadowy figure through crowded streets",
                ),
            ],
        )

    async def generate_next_scene(self, state, chosen):  # noqa: ANN001
        return _scene(scene_id="scene-2", chapter=2)


class FakeThemeRepository:
    def list_active(self) -> list[StoryTheme]:
        return [
            StoryTheme(
                theme_id="genre-noir",
                title="Noir Detective",
                tagline="Solve a crime in a rain-soaked city.",
                description="Secrets hide in every shadow.",
                image="https://example.com/noir.jpg",
                accent_color="rgba(234,179,8,0.6)",
                sort_order=10,
            )
        ]


class FakeSceneRepository:
    def list_by_story_id(self, story_id: str) -> list[StorySceneRecord]:
        return [
            StorySceneRecord(
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
                location=StorySceneLocation(
                    name="Skyline Rooftop",
                    location_type="city_rooftop",
                ),
                characters_present=["kira_voss"],
                asset_refs=StorySceneAssetRefs(
                    hero_image_id="asset_hero_001",
                    scene_image_id="asset_scene_001",
                    scene_video_id="asset_video_001",
                    scene_audio_id=None,
                ),
                generation_status=StorySceneGenerationStatus(
                    text="completed",
                    image="completed",
                    video="completed",
                ),
                created_at=utc_now(),
                updated_at=utc_now(),
            )
        ]


class FakeUserStoryRepository:
    def list_by_user_id(self, user_id: str) -> list[UserStoryRecord]:
        return [
            UserStoryRecord(
                story_id="story-fs-1",
                user_id=user_id,
                session_id=None,
                title=f"{user_id} - Neon Debt",
                genre="Cyberpunk",
                character_name="Kira Voss",
                archetype="Investigator",
                last_scene_id="scene_004",
                updated_at=utc_now(),
                choices_available=3,
                progress=70,
                cover_image="https://example.com/story-fs-1.jpg",
                last_played_at=utc_now(),
                status="active",
                theme_id="theme-cyberpunk",
                theme_title="Neon Debt",
                theme_category="Cyberpunk",
                theme_description="Corporate espionage in a flooded megacity.",
                question_count=4,
                questions_generated=["Q1", "Q2"],
                created_at=utc_now(),
            )
        ]

    def get_by_user_id_and_story_id(
        self,
        user_id: str,
        story_id: str,
    ) -> UserStoryRecord | None:
        if story_id == "missing":
            return None
        return UserStoryRecord(
            story_id=story_id,
            user_id=user_id,
            session_id=story_id,
            title="Neon Debt",
            genre="Cyberpunk",
            character_name="Kira Voss",
            archetype="Investigator",
            last_scene_id="scene_004",
            updated_at=utc_now(),
            choices_available=3,
            progress=70,
            cover_image="https://example.com/story-fs-1.jpg",
            last_played_at=utc_now(),
            status="active",
            theme_id="theme-cyberpunk",
            theme_title="Neon Debt",
            theme_category="Cyberpunk",
            theme_description="Corporate espionage in a flooded megacity.",
            question_count=4,
            questions_generated=["Q1", "Q2"],
            created_at=utc_now(),
        )


class FakeStoryDocumentRepository:
    def get_story_payload(self, user_id: str, story_id: str) -> dict[str, list[dict]]:
        return {
            "questions": [
                {
                    "questionId": "q_1",
                    "question": "What drives the hero?",
                }
            ],
            "answers": [
                {
                    "questionId": "q_1",
                    "selectedOption": "Duty",
                }
            ],
            "scenes": [
                {
                    "sceneId": "scene_001",
                    "title": "Crimson Echoes",
                }
            ],
        }


def test_start_story_creates_session_and_opening_scene() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(repository=repo, generator=FakeGenerator())

    result = asyncio.run(
        use_case.start_story(
            StartStoryCommand(
                genre="Noir",
                name="Mara Vale",
                archetype="Reluctant Detective",
                motivation="Find her missing brother",
            )
        )
    )

    assert result.session_id
    assert result.scene.metadata.scene_id == "scene-1"
    assert result.scene.metadata.chapter == 1

    stored = repo.get(result.session_id)
    assert stored is not None
    assert stored.current_scene is not None
    assert len(stored.history_log) == 1
    assert stored.history_log[0].entry_type == "scene"


def test_apply_action_appends_choice_and_next_scene() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(repository=repo, generator=FakeGenerator())

    start = asyncio.run(
        use_case.start_story(
            StartStoryCommand(
                genre="Noir",
                name="Mara Vale",
                archetype="Reluctant Detective",
                motivation="Find her missing brother",
            )
        )
    )

    action = asyncio.run(
        use_case.apply_action(ApplyActionCommand(session_id=start.session_id, choice_id="A"))
    )

    assert action.session_id == start.session_id
    assert action.scene.metadata.scene_id == "scene-2"
    assert action.scene.metadata.chapter == 2

    stored = repo.get(start.session_id)
    assert stored is not None
    assert len(stored.history_log) == 3
    assert stored.history_log[1].entry_type == "choice"
    assert stored.history_log[2].entry_type == "scene"


def test_apply_action_rejects_invalid_choice_id() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(repository=repo, generator=FakeGenerator())

    start = asyncio.run(
        use_case.start_story(
            StartStoryCommand(
                genre="Noir",
                name="Mara Vale",
                archetype="Reluctant Detective",
                motivation="Find her missing brother",
            )
        )
    )

    with pytest.raises(InvalidChoiceError):
        asyncio.run(
            use_case.apply_action(
                ApplyActionCommand(session_id=start.session_id, choice_id="INVALID")
            )
        )


def test_generate_questions_returns_four_questions() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(repository=repo, generator=FakeGenerator())

    result = asyncio.run(
        use_case.generate_questions(GenerateQuestionsCommand(theme="Cyberpunk Noir"))
    )

    assert result.theme == "Cyberpunk Noir"
    assert len(result.questions) == 4
    for q in result.questions:
        assert q.question
        assert len(q.options) == 4


def test_generate_opening_scene_returns_scene_with_choices() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(repository=repo, generator=FakeGenerator())

    result = asyncio.run(
        use_case.generate_opening_scene(
            GenerateOpeningSceneCommand(
                story_id="story_test_1",
                theme_id="cyberpunk-noir",
                character_name="Kira Voss",
                answers=[
                    QuestionAnswer(question_id="q1", question="What color is the sky?", selected_option="Crimson", image_url=""),
                    QuestionAnswer(question_id="q2", question="What drives the hero?", selected_option="Revenge", image_url=""),
                ],
            )
        )
    )

    assert result.theme == "cyberpunk-noir"
    assert result.character_name == "Kira Voss"
    assert result.scene.scene_title == "Crimson Echoes"
    assert len(result.scene.choices) == 3
    assert result.scene.choices[0].choice_id == "A"


def test_list_story_themes_returns_active_theme_views() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(
        repository=repo,
        generator=FakeGenerator(),
        theme_repository=FakeThemeRepository(),
    )

    result = use_case.list_story_themes()

    assert len(result) == 1
    assert result[0].id == "genre-noir"
    assert result[0].title == "Noir Detective"


def test_list_story_scenes_returns_scene_views() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(
        repository=repo,
        generator=FakeGenerator(),
        scene_repository=FakeSceneRepository(),
    )

    result = use_case.list_story_scenes(story_id="story_123")

    assert len(result) == 1
    assert result[0].scene_id == "scene_001"
    assert result[0].story_id == "story_123"
    assert result[0].location is not None
    assert result[0].location.name == "Skyline Rooftop"


def test_list_active_stories_reads_user_story_repository_when_available() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(
        repository=repo,
        generator=FakeGenerator(),
        user_story_repository=FakeUserStoryRepository(),
    )

    result = use_case.list_active_stories(user_id="tmduUAxT4nNHLQDWmKsb9bf58342")

    assert len(result) == 1
    assert result[0].story_id == "story-fs-1"
    assert result[0].session_id == "story-fs-1"
    assert result[0].title.endswith("Neon Debt")
    assert result[0].progress == 70
    assert result[0].status == "active"


def test_list_active_stories_falls_back_to_in_memory_sessions() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(repository=repo, generator=FakeGenerator())

    start = asyncio.run(
        use_case.start_story(
            StartStoryCommand(
                genre="Noir",
                name="Mara Vale",
                archetype="Reluctant Detective",
                motivation="Find her missing brother",
            )
        )
    )

    result = use_case.list_active_stories(user_id="dev-user")

    assert len(result) == 1
    assert result[0].story_id == start.session_id
    assert result[0].session_id == start.session_id


def test_get_story_detail_returns_firestore_story_when_available() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(
        repository=repo,
        generator=FakeGenerator(),
        user_story_repository=FakeUserStoryRepository(),
        story_doc_repository=FakeStoryDocumentRepository(),
    )

    result = use_case.get_story_detail(
        user_id="tmduUAxT4nNHLQDWmKsb9bf58342",
        story_id="story-fs-1",
    )

    assert result is not None
    assert result.story_id == "story-fs-1"
    assert result.user_id == "tmduUAxT4nNHLQDWmKsb9bf58342"
    assert result.theme_id == "theme-cyberpunk"
    assert result.question_count == 4
    assert result.questions_generated == ["Q1", "Q2"]
    assert len(result.questions) == 1
    assert len(result.answers) == 1
    assert len(result.scenes) == 1


def test_get_story_detail_returns_none_when_story_missing() -> None:
    repo = InMemoryStoryStateRepository()
    use_case = StoryEngineUseCase(
        repository=repo,
        generator=FakeGenerator(),
        user_story_repository=FakeUserStoryRepository(),
    )

    result = use_case.get_story_detail(
        user_id="tmduUAxT4nNHLQDWmKsb9bf58342",
        story_id="missing",
    )

    assert result is None
