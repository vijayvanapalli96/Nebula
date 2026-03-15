from __future__ import annotations

import base64
from uuid import uuid4

from google import genai
from google.genai import types

from app.application.errors import StoryGenerationError
from app.application.ports.interleaved_generator import (
    InterleavedGenerationRequest,
    InterleavedGenerationResult,
    InterleavedGeneratorPort,
)
from app.core.settings import Settings
from app.domain.models.composition import CompositionPart, GenerationUsage, MediaPartType

CREATIVE_SYSTEM_PROMPT = """
You are a creative director that generates cohesive multimodal story output.
Produce concise text and media-friendly artifacts in a coherent sequence.
Keep content safe and production-usable.
"""


class GeminiInterleavedGenerator(InterleavedGeneratorPort):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None
        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)

    async def generate(self, request: InterleavedGenerationRequest) -> InterleavedGenerationResult:
        if self._client is None:
            raise StoryGenerationError("GEMINI_API_KEY is not configured.")

        model_modalities = _map_model_modalities(request.requested_modalities)
        prompt = _build_generation_prompt(request)

        try:
            response = await self._client.aio.models.generate_content(
                model=self._settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=CREATIVE_SYSTEM_PROMPT,
                    temperature=0.8,
                    max_output_tokens=2048,
                    response_modalities=model_modalities,
                ),
            )
        except Exception as exc:
            raise StoryGenerationError(f"Gemini interleaved generation failed: {exc}") from exc

        parts = _extract_parts(response)
        if not parts:
            parts = [
                CompositionPart(
                    part_id=str(uuid4()),
                    type="text",
                    sequence=1,
                    status="completed",
                    content=getattr(response, "text", "").strip() or "No content generated.",
                )
            ]

        _append_placeholder_parts(parts=parts, requested_modalities=request.requested_modalities)
        usage = _extract_usage(response)
        return InterleavedGenerationResult(parts=parts[: request.max_parts], usage=usage)

    async def regenerate_part(
        self,
        request: InterleavedGenerationRequest,
        original_part: CompositionPart,
        instruction: str | None = None,
    ) -> CompositionPart:
        revised_request = InterleavedGenerationRequest(
            prompt=(
                f"{request.prompt}\n\nRegenerate part type '{original_part.type}'. "
                f"Prior content: {original_part.content or original_part.asset_uri or 'N/A'}."
                f"{f' Instruction: {instruction}.' if instruction else ''}"
            ),
            requested_modalities=[original_part.type],
            style_bible=request.style_bible,
            max_parts=1,
        )
        result = await self.generate(revised_request)
        regenerated = result.parts[0]
        regenerated.type = original_part.type
        regenerated.sequence = original_part.sequence
        regenerated.status = "completed"
        return regenerated


def _map_model_modalities(requested_modalities: list[MediaPartType]) -> list[str]:
    modalities = {"TEXT"}
    if "image" in requested_modalities:
        modalities.add("IMAGE")
    return sorted(modalities)


def _build_generation_prompt(request: InterleavedGenerationRequest) -> str:
    style_lines = []
    if request.style_bible:
        for key, value in request.style_bible.items():
            style_lines.append(f"- {key}: {value}")

    style_block = "\n".join(style_lines) if style_lines else "- none"
    modalities = ", ".join(request.requested_modalities)
    return (
        "Generate a cohesive interleaved multimedia composition.\n"
        f"Prompt: {request.prompt}\n"
        f"Target modalities: {modalities}\n"
        f"Max parts: {request.max_parts}\n"
        "Style bible:\n"
        f"{style_block}\n"
        "Return content suitable for a timeline where each chunk can be rendered as text/image/audio/video."
    )


def _extract_parts(response: types.GenerateContentResponse) -> list[CompositionPart]:
    extracted: list[CompositionPart] = []
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        text = getattr(response, "text", "")
        if text:
            extracted.append(
                CompositionPart(
                    part_id=str(uuid4()),
                    type="text",
                    sequence=1,
                    status="completed",
                    content=text.strip(),
                )
            )
        return extracted

    sequence = 1
    parts = getattr(candidates[0].content, "parts", None) or []
    for item in parts:
        text = getattr(item, "text", None)
        if text and text.strip():
            extracted.append(
                CompositionPart(
                    part_id=str(uuid4()),
                    type="text",
                    sequence=sequence,
                    status="completed",
                    content=text.strip(),
                )
            )
            sequence += 1
            continue

        inline_data = getattr(item, "inline_data", None)
        if inline_data and getattr(inline_data, "mime_type", "").startswith("image/"):
            raw_data = getattr(inline_data, "data", b"") or b""
            if isinstance(raw_data, str):
                encoded = raw_data
            else:
                encoded = base64.b64encode(raw_data).decode("utf-8")
            extracted.append(
                CompositionPart(
                    part_id=str(uuid4()),
                    type="image",
                    sequence=sequence,
                    status="completed",
                    asset_uri=f"data:{inline_data.mime_type};base64,{encoded}",
                    mime_type=inline_data.mime_type,
                )
            )
            sequence += 1

    return extracted


def _append_placeholder_parts(
    parts: list[CompositionPart],
    requested_modalities: list[MediaPartType],
) -> None:
    existing_types = {part.type for part in parts}
    sequence = len(parts) + 1
    for modality in requested_modalities:
        if modality in existing_types:
            continue
        if modality in {"audio", "video"}:
            parts.append(
                CompositionPart(
                    part_id=str(uuid4()),
                    type=modality,
                    sequence=sequence,
                    status="queued",
                    content=f"{modality.title()} render queued.",
                    metadata={"requires_background_render": True},
                )
            )
            sequence += 1


def _extract_usage(response: types.GenerateContentResponse) -> GenerationUsage:
    usage_metadata = getattr(response, "usage_metadata", None)
    prompt_tokens = getattr(usage_metadata, "prompt_token_count", 0) if usage_metadata else 0
    output_tokens = getattr(usage_metadata, "candidates_token_count", 0) if usage_metadata else 0
    image_count = 0
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        for part in getattr(candidates[0].content, "parts", None) or []:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and getattr(inline_data, "mime_type", "").startswith("image/"):
                image_count += 1
    return GenerationUsage(
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        image_count=image_count,
    )

