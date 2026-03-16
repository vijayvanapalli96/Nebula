from __future__ import annotations

import asyncio
from functools import partial

from google import genai
from google.genai import types

from app.application.errors import VideoGenerationError
from app.application.ports.video_generator import (
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoGeneratorPort,
)
from app.core.settings import Settings


class GeminiVideoGenerator(VideoGeneratorPort):
    def __init__(self, settings: Settings) -> None:
        self._client: genai.Client | None = None
        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)

    async def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        if self._client is None:
            raise VideoGenerationError("GEMINI_API_KEY is not configured.")

        config = types.GenerateVideosConfig(
            aspect_ratio=request.aspect_ratio,
            number_of_videos=1,
            duration_seconds=request.duration_seconds,
        )
        if request.negative_prompt:
            config.negative_prompt = request.negative_prompt

        try:
            # generate_videos is synchronous — run in executor to avoid blocking.
            loop = asyncio.get_running_loop()
            operation = await loop.run_in_executor(
                None,
                partial(
                    self._client.models.generate_videos,
                    model=request.model,
                    prompt=request.prompt,
                    config=config,
                ),
            )

            # Poll until done.
            while not operation.done:
                await asyncio.sleep(5)
                operation = await loop.run_in_executor(
                    None,
                    partial(self._client.operations.get, operation),
                )

        except VideoGenerationError:
            raise
        except Exception as exc:
            raise VideoGenerationError(f"Veo request failed: {exc}") from exc

        if not operation.response or not operation.response.generated_videos:
            error_detail = getattr(operation, "error", "No videos returned")
            raise VideoGenerationError(f"Veo returned no video: {error_detail}")

        video = operation.response.generated_videos[0]
        try:
            video_bytes = self._client.files.download(file=video.video)
        if not video_bytes:
            raise VideoGenerationError("Veo download returned empty bytes")
        except Exception as exc:
            raise VideoGenerationError(f"Failed to download video: {exc}") from exc

        return VideoGenerationResult(
            video_bytes=video_bytes,
            file_size_bytes=len(video_bytes),
            duration_seconds=request.duration_seconds,
        )
