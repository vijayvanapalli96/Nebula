from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.video_commands import GenerateVideoCommand
from app.application.dto.video_results import VideoJobResult
from app.application.errors import VideoJobNotFoundError
from app.application.ports.video_generator import VideoGenerationRequest, VideoGeneratorPort
from app.domain.models.video import VideoJob
from app.domain.repositories.video_repository import VideoJobRepository

# Cost per second by model (USD).
_COST_PER_SECOND: dict[str, float] = {
    "veo-2.0-generate-001": 0.35,
    "veo-3.0-generate-001": 0.40,
    "veo-3.0-fast-generate-001": 0.15,
    "veo-3.1-generate-preview": 0.40,
    "veo-3.1-fast-generate-preview": 0.15,
}


class VideoGenerationUseCase:
    def __init__(
        self,
        repository: VideoJobRepository,
        generator: VideoGeneratorPort,
    ) -> None:
        self._repository = repository
        self._generator = generator

    async def generate_video(self, command: GenerateVideoCommand) -> VideoJobResult:
        job = VideoJob(
            job_id=str(uuid4()),
            prompt=command.prompt.strip(),
            model=command.model,
            status="generating",
            duration_seconds=command.duration_seconds,
            aspect_ratio=command.aspect_ratio,
            negative_prompt=command.negative_prompt,
            cost_estimate=self._estimate_cost(command.model, command.duration_seconds),
        )
        self._repository.create(job)

        try:
            result = await self._generator.generate(
                VideoGenerationRequest(
                    prompt=command.prompt,
                    model=command.model,
                    duration_seconds=command.duration_seconds,
                    aspect_ratio=command.aspect_ratio,
                    negative_prompt=command.negative_prompt,
                )
            )
            video_path = f"generated_videos/{job.job_id}.mp4"
            with open(video_path, "wb") as f:
                f.write(result.video_bytes)

            job.status = "completed"
            job.video_uri = video_path
            job.file_size_bytes = result.file_size_bytes
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)

        job.updated_at = datetime.now(UTC)
        self._repository.save(job)
        return self._to_result(job)

    def get_job(self, job_id: str) -> VideoJobResult:
        job = self._repository.get(job_id)
        if job is None:
            raise VideoJobNotFoundError(f"Video job '{job_id}' not found.")
        return self._to_result(job)

    def list_jobs(self) -> list[VideoJobResult]:
        jobs = sorted(
            self._repository.list_all(),
            key=lambda j: j.created_at,
            reverse=True,
        )
        return [self._to_result(j) for j in jobs]

    @staticmethod
    def _estimate_cost(model: str, duration_seconds: int) -> float:
        rate = _COST_PER_SECOND.get(model, 0.15)
        return round(rate * duration_seconds, 2)

    @staticmethod
    def _to_result(job: VideoJob) -> VideoJobResult:
        return VideoJobResult(
            job_id=job.job_id,
            status=job.status,
            prompt=job.prompt,
            model=job.model,
            duration_seconds=job.duration_seconds,
            aspect_ratio=job.aspect_ratio,
            video_uri=job.video_uri,
            file_size_bytes=job.file_size_bytes,
            cost_estimate=job.cost_estimate,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
