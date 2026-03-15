from __future__ import annotations

import asyncio

import pytest

from app.application.dto.story_commands import ApplyActionCommand, GenerateOpeningSceneCommand, GenerateQuestionsCommand, QuestionAnswer, StartStoryCommand
from app.application.errors import InvalidChoiceError
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.domain.models.story import InitialQuestion, OpeningChoice, OpeningScene, QuestionOption, Scene, SceneChoice, SceneMetadata, StoryTheme
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
                theme="Cyberpunk Noir",
                character_name="Kira Voss",
                answers=[
                    QuestionAnswer(question="What color is the sky?", answer="Crimson"),
                    QuestionAnswer(question="What drives the hero?", answer="Revenge"),
                ],
            )
        )
    )

    assert result.theme == "Cyberpunk Noir"
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
