from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StartStoryCommand:
    genre: str
    name: str
    archetype: str
    motivation: str


@dataclass(frozen=True)
class GenerateQuestionsCommand:
    theme: str


@dataclass(frozen=True)
class GenerateStoryQuestionsCommand:
    user_id: str
    theme_id: str


@dataclass(frozen=True)
class QuestionAnswer:
    question_id: str
    question: str
    selected_option: str
    image_url: str


@dataclass(frozen=True)
class GenerateOpeningSceneCommand:
    story_id: str
    theme_id: str
    character_name: str
    answers: list[QuestionAnswer]
    custom_input: str = ""


@dataclass(frozen=True)
class ApplyActionCommand:
    session_id: str
    choice_id: str


@dataclass(frozen=True)
class GenerateContinuationCommand:
    """Input for the scene-continuation block.

    Matches the contract agreed with the story-start PR:
      story_id, previous_scene_id, current_scene_id, choice_id
    """
    story_id: str
    previous_scene_id: str
    current_scene_id: str
    choice_id: str

