from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StartStoryCommand:
    genre: str
    name: str
    archetype: str
    motivation: str


@dataclass(frozen=True)
class ApplyActionCommand:
    session_id: str
    choice_id: str

