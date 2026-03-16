"""Rich theme model carrying all fields needed for themed question generation."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PromptHints:
    narrative_style: str = ""
    visual_style: str = ""


@dataclass(frozen=True)
class ThemeDetail:
    theme_id: str
    title: str
    category: str
    description: str
    image_url: str = ""
    default_tone_tags: tuple[str, ...] = field(default_factory=tuple)
    prompt_hints: PromptHints = field(default_factory=PromptHints)
    is_active: bool = True
