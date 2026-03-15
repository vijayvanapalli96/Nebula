from __future__ import annotations

import asyncio

import pytest

from app.application.dto.story_commands import ApplyActionCommand, GenerateOpeningSceneCommand, GenerateQuestionsCommand, QuestionAnswer, StartStoryCommand
from app.application.errors import InvalidChoiceError
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.domain.models.story import InitialQuestion, OpeningChoice, OpeningScene, Scene, SceneChoice, SceneMetadata
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
                options=["Crimson", "Silver", "Emerald", "Obsidian"],
            ),
            InitialQuestion(
                question="What drives the hero?",
                options=["Revenge", "Curiosity", "Love", "Duty"],
            ),
            InitialQuestion(
                question="What lurks in the shadows?",
                options=["Ghosts", "Machines", "Beasts", "Nothing"],
            ),
            InitialQuestion(
                question="How does the story end?",
                options=["In flames", "With a whisper", "With a dance", "With silence"],
            ),
        ]

    async def generate_opening_scene(self, state):  # noqa: ANN001
        return _scene(scene_id="scene-1", chapter=1)

    async def generate_opening_scene_from_answers(
        self, theme, character_name, answers  # noqa: ANN001
    ):
        return OpeningScene(
            scene_title="Crimson Echoes",
            scene_description="The neon-soaked city pulses beneath you.",
            choices=[
                OpeningChoice(choice_id="A", choice_text="Enter the alley", direction_hint="Danger awaits"),
                OpeningChoice(choice_id="B", choice_text="Climb the tower", direction_hint="A broader view"),
                OpeningChoice(choice_id="C", choice_text="Follow the stranger", direction_hint="Mystery deepens"),
            ],
        )

    async def generate_next_scene(self, state, chosen):  # noqa: ANN001
        return _scene(scene_id="scene-2", chapter=2)


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
