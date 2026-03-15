from __future__ import annotations

from typing import Protocol

from app.domain.models.video import VideoJob


class VideoJobRepository(Protocol):
    def create(self, job: VideoJob) -> None:
        ...

    def get(self, job_id: str) -> VideoJob | None:
        ...

    def save(self, job: VideoJob) -> None:
        ...

    def list_all(self) -> list[VideoJob]:
        ...
