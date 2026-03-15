from __future__ import annotations

from typing import Protocol

from app.domain.models.story import InitialQuestion, Scene, SceneChoice, StoryState


class StoryGeneratorPort(Protocol):
    async def generate_initial_questions(self, theme: str) -> list[InitialQuestion]:
        ...

    async def generate_opening_scene(self, state: StoryState) -> Scene:
        ...

    async def generate_next_scene(self, state: StoryState, chosen: SceneChoice) -> Scene:
        ...

