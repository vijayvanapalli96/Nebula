from __future__ import annotations

from typing import Protocol

from app.domain.models.story import InitialQuestion, OpeningScene, Scene, SceneChoice, StoryState
from app.domain.models.theme_detail import ThemeDetail


class StoryGeneratorPort(Protocol):
    async def generate_initial_questions(self, theme: str) -> list[InitialQuestion]:
        ...

    async def generate_option_image(self, prompt: str) -> bytes:
        """Generate an image from a text prompt. Returns PNG bytes."""
        ...

    async def generate_option_image_grid(self, prompts: list[str]) -> bytes:
        """Generate a 2x2 grid image from four prompts. Returns PNG bytes."""
        ...

    async def generate_opening_scene(self, state: StoryState) -> Scene:
        ...

    async def generate_opening_scene_from_answers(
        self, theme: ThemeDetail, character_name: str, answers: list[tuple[str, str]]
    ) -> OpeningScene:
        ...

    async def generate_next_scene(self, state: StoryState, chosen: SceneChoice) -> Scene:
        ...

