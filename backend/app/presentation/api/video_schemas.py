from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.application.dto.video_commands import GenerateVideoCommand
from app.application.dto.video_results import VideoJobResult


# ── Requests ──


class VideoGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Text prompt for video generation.")
    duration_seconds: int = Field(default=4, ge=4, le=8, description="Video length (4-8 seconds).")
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        default="16:9", description="Output aspect ratio."
    )
    model: str = Field(
        default="veo-3.0-fast-generate-001",
        description="Veo model to use.",
    )
    negative_prompt: str | None = Field(default=None, description="What to avoid in the video.")


# ── Responses ──


class VideoJobResponse(BaseModel):
    job_id: str
    status: str
    prompt: str
    model: str
    duration_seconds: int
    aspect_ratio: str
    video_uri: str | None = None
    file_size_bytes: int = 0
    cost_estimate: float = 0.0
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class VideoJobListResponse(BaseModel):
    jobs: list[VideoJobResponse]
    total: int


# ── Mappers ──


def to_generate_video_command(request: VideoGenerateRequest) -> GenerateVideoCommand:
    return GenerateVideoCommand(
        prompt=request.prompt,
        duration_seconds=request.duration_seconds,
        aspect_ratio=request.aspect_ratio,
        model=request.model,
        negative_prompt=request.negative_prompt,
    )


def to_video_job_response(result: VideoJobResult) -> VideoJobResponse:
    return VideoJobResponse(
        job_id=result.job_id,
        status=result.status,
        prompt=result.prompt,
        model=result.model,
        duration_seconds=result.duration_seconds,
        aspect_ratio=result.aspect_ratio,
        video_uri=result.video_uri,
        file_size_bytes=result.file_size_bytes,
        cost_estimate=result.cost_estimate,
        error_message=result.error_message,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
