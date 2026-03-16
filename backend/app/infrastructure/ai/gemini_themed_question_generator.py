"""Gemini-backed implementation of ThemedQuestionGeneratorPort.

Uses ``THEMED_QUESTIONS_SYSTEM_PROMPT`` and ``build_themed_questions_prompt``
to generate questions that are deeply rooted in the provided ThemeDetail.
"""
from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.application.errors import StoryGenerationError
from app.application.ports.themed_question_generator import ThemedQuestionGeneratorPort
from app.core.settings import Settings
from app.domain.models.story import InitialQuestion, QuestionOption
from app.domain.models.theme_detail import ThemeDetail
from app.infrastructure.ai.prompts import (
    THEMED_QUESTIONS_SYSTEM_PROMPT,
    build_themed_questions_prompt,
)


# ── Pydantic response-parsing helpers ─────────────────────────────────────────


class _OptionPayload(BaseModel):
    text: str
    image_prompt: str


class _QuestionPayload(BaseModel):
    id: str = ""
    question: str
    story_influence: str = ""
    options: list[_OptionPayload] = Field(..., min_length=4, max_length=4)


class _QuestionsPayload(BaseModel):
    questions: list[_QuestionPayload] = Field(..., min_length=1, max_length=8)


# ── Generator ─────────────────────────────────────────────────────────────────


class GeminiThemedQuestionGenerator:
    """Generates story-setup questions tailored to a full ThemeDetail object."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None
        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_themed_questions(self, theme: ThemeDetail) -> list[InitialQuestion]:
        if self._client is None:
            raise StoryGenerationError("GEMINI_API_KEY is not configured.")

        prompt = build_themed_questions_prompt(theme)
        try:
            response = await self._client.aio.models.generate_content(
                model=self._settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=THEMED_QUESTIONS_SYSTEM_PROMPT,
                    temperature=0.9,
                    top_p=0.95,
                    max_output_tokens=2000,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            raise StoryGenerationError(f"Gemini themed-questions request failed: {exc}") from exc

        raw_text = _extract_response_text(response)
        payload = _parse_model_json(raw_text)

        try:
            parsed = _QuestionsPayload.model_validate(payload)
        except Exception as exc:
            raise StoryGenerationError(
                f"Gemini returned invalid themed-questions schema: {exc}"
            ) from exc

        return [
            InitialQuestion(
                question=q.question,
                question_id=q.id,
                options=[
                    QuestionOption(text=opt.text, image_prompt=opt.image_prompt)
                    for opt in q.options
                ],
            )
            for q in parsed.questions
        ]


# ── Private helpers ────────────────────────────────────────────────────────────


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

    raise StoryGenerationError("Gemini themed-questions response contained no text.")


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
            raise StoryGenerationError("Gemini themed-questions output was not valid JSON.")
        try:
            return json.loads(raw[start: end + 1])
        except json.JSONDecodeError as exc:
            raise StoryGenerationError(
                "Gemini themed-questions JSON parsing failed."
            ) from exc
