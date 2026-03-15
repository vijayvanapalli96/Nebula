from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types

from config import Settings
from prompts import (
    SYSTEM_PROMPT,
    append_style_seed,
    build_action_prompt,
    build_opening_prompt,
)
from schemas import SceneChoice, SceneResponse, StoryState


class StoryGenerationError(RuntimeError):
    pass


class GeminiStoryGenerator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None

        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_opening_scene(self, state: StoryState) -> SceneResponse:
        prompt = build_opening_prompt(state)
        return await self._generate_scene(prompt, genre=state.genre)

    async def generate_next_scene(self, state: StoryState, chosen: SceneChoice) -> SceneResponse:
        prompt = build_action_prompt(state, chosen)
        return await self._generate_scene(prompt, genre=state.genre)

    async def _generate_scene(self, prompt: str, genre: str) -> SceneResponse:
        if self._client is None:
            raise StoryGenerationError("GEMINI_API_KEY is not configured.")

        try:
            response = await self._client.aio.models.generate_content(
                model=self._settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.85,
                    top_p=0.95,
                    max_output_tokens=900,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            raise StoryGenerationError(f"Gemini request failed: {exc}") from exc

        raw_text = _extract_response_text(response)
        payload = _parse_model_json(raw_text)

        try:
            scene = SceneResponse.model_validate(payload)
        except Exception as exc:
            raise StoryGenerationError(f"Gemini returned invalid scene schema: {exc}") from exc

        scene.visual_prompt = append_style_seed(genre=genre, visual_prompt=scene.visual_prompt)
        return scene


def _extract_response_text(response: Any) -> str:
    text = getattr(response, "text", "")
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    if candidates:
        parts = (
            getattr(candidates[0], "content", None)
            and getattr(candidates[0].content, "parts", None)
        ) or []
        for part in parts:
            if hasattr(part, "text") and part.text:
                return part.text

    raise StoryGenerationError("Gemini response did not contain text content.")


def _parse_model_json(raw_text: str) -> dict[str, Any]:
    raw = raw_text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise StoryGenerationError("Gemini output was not valid JSON.")
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError as exc:
            raise StoryGenerationError("Gemini output JSON parsing failed.") from exc
