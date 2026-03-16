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
    story_id: str
    session_id: str
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None
    updated_at: datetime
    choices_available: int
    progress: int | None = None
    cover_image: str | None = None
    last_played_at: datetime | None = None
    status: str | None = None


@dataclass(frozen=True)
class StoryDetailView:
    story_id: str
    user_id: str
    session_id: str
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None
    updated_at: datetime
    choices_available: int
    progress: int | None = None
    cover_image: str | None = None
    last_played_at: datetime | None = None
    status: str | None = None
    theme_id: str | None = None
    theme_title: str | None = None
    theme_category: str | None = None
    theme_description: str | None = None
    question_count: int | None = None
    questions_generated: list[str] | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class StoryThemeView:
    id: str
    title: str
    tagline: str
    description: str
    image: str
    accent_color: str


@dataclass(frozen=True)
class StorySceneLocationView:
    name: str
    location_type: str


@dataclass(frozen=True)
class StorySceneAssetRefsView:
    hero_image_id: str | None
    scene_image_id: str | None
    scene_video_id: str | None
    scene_audio_id: str | None


@dataclass(frozen=True)
class StorySceneGenerationStatusView:
    text: str
    image: str
    video: str


@dataclass(frozen=True)
class StorySceneView:
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
    location: StorySceneLocationView | None
    characters_present: list[str]
    asset_refs: StorySceneAssetRefsView
    generation_status: StorySceneGenerationStatusView
    created_at: datetime
    updated_at: datetime
