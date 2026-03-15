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


@dataclass
class InitialQuestion:
    question: str
    options: list[QuestionOption]


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

