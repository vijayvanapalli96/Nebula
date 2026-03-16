from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.application.dto.video_results import VideoJobResult
from app.main import create_app
from app.presentation.api.dependencies import get_video_use_case, require_auth


class FakeVideoUseCase:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self._job = VideoJobResult(
            job_id="video-1",
            status="completed",
            prompt="A spaceship in a nebula.",
            model="veo-3.0-fast-generate-001",
            duration_seconds=4,
            aspect_ratio="16:9",
            video_uri="generated_videos/video-1.mp4",
            file_size_bytes=2048,
            cost_estimate=0.60,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    async def generate_video(self, command):  # noqa: ANN001
        return self._job

    def get_job(self, job_id: str) -> VideoJobResult:
        return self._job

    def list_jobs(self) -> list[VideoJobResult]:
        return [self._job]


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_video_use_case] = lambda: FakeVideoUseCase()
    app.dependency_overrides[require_auth] = lambda: "test-user"
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_generate_video_endpoint(client: TestClient) -> None:
    response = client.post(
        "/v1/videos/generate",
        json={
            "prompt": "A cinematic shot of a spaceship in a nebula.",
            "duration_seconds": 4,
            "aspect_ratio": "16:9",
            "model": "veo-3.0-fast-generate-001",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["job_id"] == "video-1"
    assert body["status"] == "completed"
    assert body["cost_estimate"] == 0.60


def test_get_video_job_endpoint(client: TestClient) -> None:
    response = client.get("/v1/videos/video-1")
    assert response.status_code == 200
    assert response.json()["job_id"] == "video-1"


def test_list_video_jobs_endpoint(client: TestClient) -> None:
    response = client.get("/v1/videos")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["jobs"]) == 1
