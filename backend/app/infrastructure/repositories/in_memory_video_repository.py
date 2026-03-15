from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock

from app.domain.models.video import VideoJob
from app.domain.repositories.video_repository import VideoJobRepository


class InMemoryVideoJobRepository(VideoJobRepository):
    def __init__(self) -> None:
        self._jobs: dict[str, VideoJob] = {}
        self._lock = RLock()

    def create(self, job: VideoJob) -> None:
        with self._lock:
            self._jobs[job.job_id] = deepcopy(job)

    def get(self, job_id: str) -> VideoJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return deepcopy(job) if job is not None else None

    def save(self, job: VideoJob) -> None:
        with self._lock:
            job.updated_at = datetime.now(UTC)
            self._jobs[job.job_id] = deepcopy(job)

    def list_all(self) -> list[VideoJob]:
        with self._lock:
            return [deepcopy(j) for j in self._jobs.values()]
