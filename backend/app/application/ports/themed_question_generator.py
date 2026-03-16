"""Port protocol for LLM-based themed question generation."""
from __future__ import annotations

from typing import Protocol

from app.domain.models.story import InitialQuestion
from app.domain.models.theme_detail import ThemeDetail


class ThemedQuestionGeneratorPort(Protocol):
    async def generate_themed_questions(self, theme: ThemeDetail) -> list[InitialQuestion]:
        """Generate exactly 4 story-setup questions tailored to the given theme."""
        ...
