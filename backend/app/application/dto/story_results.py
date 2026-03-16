from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.models.story import InitialQuestion, OpeningScene, Scene


@dataclass(frozen=True)
class QuestionsResult:
    theme: str
    questions: list[InitialQuestion]


@dataclass(frozen=True)
class GenerateStoryQuestionsResult:
    story_id: str
    theme: str
    questions: list[InitialQuestion]


@dataclass(frozen=True)
class OpeningSceneResult:
    story_id: str
    theme: str
    character_name: str
    scene: OpeningScene


@dataclass(frozen=True)
class StoryStartResult:
    session_id: str
    scene: Scene


@dataclass(frozen=True)
class StoryActionResult:
    session_id: str
    scene: Scene


@dataclass(frozen=True)
class StoryCardView:
    session_id: str
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None
    updated_at: datetime
    choices_available: int


@dataclass(frozen=True)
class StoryThemeView:
    id: str
    title: str
    tagline: str
    description: str
    image: str
    accent_color: str
