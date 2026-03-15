from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class SceneMetadata(BaseModel):
    scene_id: str = Field(..., description="Unique scene identifier.")
    chapter: int = Field(..., ge=1, description="Story chapter/turn index.")
    mood: str = Field(..., min_length=1, description="Current tone of the scene.")
    tension: int = Field(..., ge=0, le=100, description="Tension score from 0 to 100.")


class SceneChoice(BaseModel):
    choice_id: str = Field(..., description="Frontend-visible choice identifier.")
    label: str = Field(..., min_length=1, description="Choice label shown to the player.")
    consequence_hint: str | None = Field(
        default=None,
        description="Optional short hint about likely consequence.",
    )


class SceneResponse(BaseModel):
    metadata: SceneMetadata
    visual_prompt: str = Field(..., min_length=1, description="Image generation prompt.")
    narrative_text: str = Field(..., min_length=1, description="Cinematic scene prose.")
    choices: list[SceneChoice] = Field(..., min_length=2, max_length=4)


class HistoryEntry(BaseModel):
    turn: int = Field(..., ge=1)
    entry_type: Literal["scene", "choice"]
    content: str = Field(..., min_length=1)
    choice_id: str | None = None
    scene_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class StoryState(BaseModel):
    session_id: str
    genre: str
    character_name: str
    archetype: str
    motivation: str
    history_log: list[HistoryEntry] = Field(default_factory=list)
    current_scene: SceneResponse | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class StoryStartRequest(BaseModel):
    genre: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    archetype: str = Field(..., min_length=1)
    motivation: str = Field(..., min_length=1)


class StoryStartResponse(BaseModel):
    session_id: str
    scene: SceneResponse


class StoryActionRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    choice_id: str = Field(..., min_length=1)


class StoryActionResponse(BaseModel):
    session_id: str
    scene: SceneResponse


class StoryCard(BaseModel):
    session_id: str
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None = None
    updated_at: datetime
    choices_available: int = 0
