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
    question: str
    answer: str


@dataclass(frozen=True)
class GenerateOpeningSceneCommand:
    theme: str
    character_name: str
    answers: list[QuestionAnswer]


@dataclass(frozen=True)
class ApplyActionCommand:
    session_id: str
    choice_id: str

