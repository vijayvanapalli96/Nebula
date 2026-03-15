from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.application.dto.video_commands import GenerateVideoCommand
from app.application.ports.video_generator import (
    VideoGenerationRequest,
    VideoGenerationResult,
)
from app.application.use_cases.video_generation import VideoGenerationUseCase
from app.infrastructure.repositories.in_memory_video_repository import InMemoryVideoJobRepository


class FakeVideoGenerator:
    async def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        return VideoGenerationResult(
            video_bytes=b"\x00" * 1024,
            file_size_bytes=1024,
            duration_seconds=request.duration_seconds,
        )


class FailingVideoGenerator:
    async def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        raise RuntimeError("Veo API unavailable")


def _build_use_case(
    generator: FakeVideoGenerator | FailingVideoGenerator | None = None,
) -> VideoGenerationUseCase:
    return VideoGenerationUseCase(
        repository=InMemoryVideoJobRepository(),
        generator=generator or FakeVideoGenerator(),
    )


def test_generate_video_creates_job_and_file() -> None:
    use_case = _build_use_case()
    result = asyncio.run(
        use_case.generate_video(
            GenerateVideoCommand(
                prompt="A spaceship flying through a nebula.",
                duration_seconds=4,
                model="veo-3.0-fast-generate-001",
            )
        )
    )

    assert result.status == "completed"
    assert result.file_size_bytes == 1024
    assert result.video_uri is not None
    assert result.cost_estimate == 0.60  # $0.15 * 4s


def test_generate_video_records_failure() -> None:
    use_case = _build_use_case(generator=FailingVideoGenerator())
    result = asyncio.run(
        use_case.generate_video(
            GenerateVideoCommand(prompt="A sunset over the ocean.", duration_seconds=4)
        )
    )

    assert result.status == "failed"
    assert result.error_message is not None
    assert "unavailable" in result.error_message.lower()


def test_list_and_get_jobs() -> None:
    use_case = _build_use_case()

    result = asyncio.run(
        use_case.generate_video(
            GenerateVideoCommand(prompt="Forest scene.", duration_seconds=4)
        )
    )

    fetched = use_case.get_job(result.job_id)
    assert fetched.job_id == result.job_id
    assert fetched.status == "completed"

    all_jobs = use_case.list_jobs()
    assert len(all_jobs) == 1
