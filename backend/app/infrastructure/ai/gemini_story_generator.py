from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.application.errors import StoryGenerationError
from app.application.ports.story_generator import StoryGeneratorPort
from app.core.settings import Settings
from app.domain.models.story import InitialQuestion, Scene, SceneChoice, SceneMetadata, StoryState
from app.infrastructure.ai.prompts import (
    INITIAL_QUESTIONS_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    append_style_seed,
    build_action_prompt,
    build_opening_prompt,
    build_questions_prompt,
)


class _QuestionPayload(BaseModel):
    question: str
    options: list[str] = Field(..., min_length=4, max_length=4)


class _QuestionsPayload(BaseModel):
    questions: list[_QuestionPayload] = Field(..., min_length=1, max_length=8)


class _SceneMetadataPayload(BaseModel):
    scene_id: str
    chapter: int = Field(..., ge=1)
    mood: str
    tension: int = Field(..., ge=0, le=100)


class _SceneChoicePayload(BaseModel):
    choice_id: str
    label: str
    consequence_hint: str | None = None


class _ScenePayload(BaseModel):
    metadata: _SceneMetadataPayload
    visual_prompt: str
    narrative_text: str
    choices: list[_SceneChoicePayload] = Field(..., min_length=2, max_length=4)


class GeminiStoryGenerator(StoryGeneratorPort):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None
        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_initial_questions(self, theme: str) -> list[InitialQuestion]:
        if self._client is None:
            raise StoryGenerationError("GEMINI_API_KEY is not configured.")

        prompt = build_questions_prompt(theme)
        try:
            response = await self._client.aio.models.generate_content(
                model=self._settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=INITIAL_QUESTIONS_SYSTEM_PROMPT,
                    temperature=0.9,
                    top_p=0.95,
                    max_output_tokens=800,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            raise StoryGenerationError(f"Gemini request failed: {exc}") from exc

        raw_text = _extract_response_text(response)
        payload = _parse_model_json(raw_text)

        try:
            questions_payload = _QuestionsPayload.model_validate(payload)
        except Exception as exc:
            raise StoryGenerationError(f"Gemini returned invalid questions schema: {exc}") from exc

        return [
            InitialQuestion(question=q.question, options=list(q.options))
            for q in questions_payload.questions
        ]

    async def generate_opening_scene(self, state: StoryState) -> Scene:
        prompt = build_opening_prompt(state)
        return await self._generate_scene(prompt=prompt, genre=state.genre)

    async def generate_next_scene(self, state: StoryState, chosen: SceneChoice) -> Scene:
        prompt = build_action_prompt(state, chosen=chosen)
        return await self._generate_scene(prompt=prompt, genre=state.genre)

    async def _generate_scene(self, prompt: str, genre: str) -> Scene:
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
            scene_payload = _ScenePayload.model_validate(payload)
        except Exception as exc:
            raise StoryGenerationError(f"Gemini returned invalid scene schema: {exc}") from exc

        return _to_domain_scene(scene_payload=scene_payload, genre=genre)


def _to_domain_scene(scene_payload: _ScenePayload, genre: str) -> Scene:
    return Scene(
        metadata=SceneMetadata(
            scene_id=scene_payload.metadata.scene_id,
            chapter=scene_payload.metadata.chapter,
            mood=scene_payload.metadata.mood,
            tension=scene_payload.metadata.tension,
        ),
        visual_prompt=append_style_seed(
            genre=genre,
            visual_prompt=scene_payload.visual_prompt,
        ),
        narrative_text=scene_payload.narrative_text,
        choices=[
            SceneChoice(
                choice_id=choice.choice_id,
                label=choice.label,
                consequence_hint=choice.consequence_hint,
            )
            for choice in scene_payload.choices
        ],
    )


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

