from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

HistoryEntryType = Literal["scene", "choice"]


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class SceneMetadata:
    scene_id: str
    chapter: int
    mood: str
    tension: int


@dataclass
class SceneChoice:
    choice_id: str
    label: str
    consequence_hint: str | None = None


@dataclass
class Scene:
    metadata: SceneMetadata
    visual_prompt: str
    narrative_text: str
    choices: list[SceneChoice]


@dataclass
class HistoryEntry:
    turn: int
    entry_type: HistoryEntryType
    content: str
    choice_id: str | None = None
    scene_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class QuestionOption:
    text: str
    image_prompt: str
    image_uri: str | None = None
    gcs_path: str | None = None


@dataclass
class InitialQuestion:
    question: str
    options: list[QuestionOption]
    question_id: str = ""


@dataclass
class OpeningChoice:
    choice_id: str
    choice_text: str
    direction_hint: str
    image_prompt: str = ""
    image_uri: str | None = None
    video_prompt: str = ""
    video_uri: str | None = None


@dataclass
class OpeningScene:
    scene_title: str
    scene_description: str
    choices: list[OpeningChoice]
    video_prompt: str = ""
    video_uri: str | None = None


@dataclass
class StoryState:
    session_id: str
    genre: str
    character_name: str
    archetype: str
    motivation: str
    history_log: list[HistoryEntry] = field(default_factory=list)
    current_scene: Scene | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class StoryTheme:
    theme_id: str
    title: str
    tagline: str
    description: str
    image: str
    accent_color: str
    is_active: bool = True
    sort_order: int = 0
    is_active: bool = True
    sort_order: int = 0
