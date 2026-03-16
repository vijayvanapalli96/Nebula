"""Domain models for persisted story documents and their sub-collections."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class StoredQuestionOption:
    text: str
    image_prompt: str
    image_url: str = ""
    gcs_path: str = ""


@dataclass
class StoredQuestion:
    question_id: str
    question: str
    options: list[StoredQuestionOption] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)


@dataclass
class StoryDocument:
    story_id: str
    user_id: str
    theme_id: str
    theme_title: str
    theme_category: str
    theme_description: str
    theme_image_url: str = ""
    status: str = "initializing"
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)
    questions_generated: bool = False
    question_count: int = 0
