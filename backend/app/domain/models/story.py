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
    summary: str = ""


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
class StorySceneLocation:
    name: str
    location_type: str


@dataclass(frozen=True)
class StorySceneAssetRefs:
    hero_image_id: str | None = None
    scene_image_id: str | None = None
    scene_video_id: str | None = None
    scene_audio_id: str | None = None


@dataclass(frozen=True)
class StorySceneGenerationStatus:
    text: str = "pending"
    image: str = "pending"
    video: str = "pending"


@dataclass(frozen=True)
class StorySceneRecord:
    scene_id: str
    story_id: str
    chapter_number: int
    scene_number: int
    title: str
    description: str
    short_summary: str
    full_narrative: str
    parent_scene_id: str | None
    selected_choice_id_from_parent: str | None
    path_depth: int
    is_root: bool
    is_current_checkpoint: bool
    is_ending: bool
    ending_type: str | None
    scene_type: str
    mood: str
    location: StorySceneLocation | None
    characters_present: list[str]
    asset_refs: StorySceneAssetRefs
    generation_status: StorySceneGenerationStatus
    created_at: datetime
    updated_at: datetime


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


@dataclass(frozen=True)
class UserStoryRecord:
    story_id: str
    user_id: str
    session_id: str | None
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None
    updated_at: datetime
    choices_available: int = 0
    progress: int | None = None
    cover_image: str | None = None
    last_played_at: datetime | None = None
    status: str | None = None
    theme_id: str | None = None
    theme_title: str | None = None
    theme_category: str | None = None
    theme_description: str | None = None
    question_count: int | None = None
    questions_generated: list[str] = field(default_factory=list)
    created_at: datetime | None = None
