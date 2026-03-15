from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.application.dto.creative_results import ExportResult
from app.domain.models.composition import (
    AssetRecord,
    Composition,
    CompositionPart,
    GenerationUsage,
    Project,
)
from app.main import create_app
from app.presentation.api.dependencies import get_creative_use_case


def _sample_composition() -> Composition:
    now = datetime.now(UTC)
    return Composition(
        composition_id="comp-1",
        project_id="project-1",
        prompt="Create an educational social post with visuals.",
        target_platform="instagram",
        status="partial",
        requested_modalities=["text", "image", "audio", "video"],
        parts=[
            CompositionPart(
                part_id="part-1",
                type="text",
                sequence=1,
                status="completed",
                content="A quick explainer script.",
                created_at=now,
                updated_at=now,
            ),
            CompositionPart(
                part_id="part-2",
                type="image",
                sequence=2,
                status="completed",
                asset_uri="https://cdn.example.com/frame-1.png",
                mime_type="image/png",
                created_at=now,
                updated_at=now,
            ),
            CompositionPart(
                part_id="part-3",
                type="audio",
                sequence=3,
                status="queued",
                content="Audio render queued.",
                created_at=now,
                updated_at=now,
            ),
        ],
        version=1,
        usage=GenerationUsage(prompt_tokens=40, output_tokens=120, image_count=1),
        created_at=now,
        updated_at=now,
    )


class FakeCreativeUseCase:
    def __init__(self) -> None:
        self._composition = _sample_composition()

    def create_project(self, command):  # noqa: ANN001
        now = datetime.now(UTC)
        return Project(
            project_id="project-1",
            title=command.title,
            use_case=command.use_case,
            tone=command.tone,
            style_bible=command.style_bible,
            created_at=now,
            updated_at=now,
        )

    async def create_composition(self, command):  # noqa: ANN001
        self._composition.prompt = command.prompt
        return self._composition

    def get_composition(self, composition_id: str) -> Composition:
        return self._composition

    def build_stream_events(self, composition_id: str) -> list[dict[str, str]]:
        return [
            {"event": "composition_status", "data": "comp-1|partial|v1"},
            {"event": "part", "data": "part-1|text|completed|A quick explainer script."},
            {"event": "done", "data": "comp-1"},
        ]

    async def regenerate_part(self, command):  # noqa: ANN001
        self._composition.version += 1
        self._composition.parts[0].content = command.instruction or "Regenerated text."
        self._composition.parts[0].updated_at = datetime.now(UTC)
        self._composition.updated_at = datetime.now(UTC)
        return self._composition

    def create_asset_upload(self, command):  # noqa: ANN001
        now = datetime.now(UTC)
        return AssetRecord(
            asset_id="asset-1",
            filename=command.filename,
            mime_type=command.mime_type,
            upload_url="https://storage.googleapis.com/upload/asset-1",
            storage_uri="gs://creative-story-assets/asset-1/file.png",
            expires_at=now + timedelta(minutes=30),
            created_at=now,
            updated_at=now,
        )

    def get_asset(self, asset_id: str) -> AssetRecord:
        now = datetime.now(UTC)
        return AssetRecord(
            asset_id=asset_id,
            filename="asset.png",
            mime_type="image/png",
            upload_url="https://storage.googleapis.com/upload/asset-1",
            storage_uri="gs://creative-story-assets/asset-1/file.png",
            expires_at=now + timedelta(minutes=30),
            status="ready",
            created_at=now,
            updated_at=now,
        )

    def export_composition(self, command):  # noqa: ANN001
        return ExportResult(
            export_id="export-1",
            composition_id=command.composition_id,
            export_format=command.export_format,
            download_url="https://storage.googleapis.com/creative-story-exports/file.zip",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

    def get_usage(self) -> GenerationUsage:
        return GenerationUsage(prompt_tokens=100, output_tokens=240, image_count=2)


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_creative_use_case] = lambda: FakeCreativeUseCase()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_project_endpoint(client: TestClient) -> None:
    response = client.post(
        "/v1/projects",
        json={
            "title": "Campaign Alpha",
            "use_case": "marketing_asset_generator",
            "tone": "bold",
            "style_bible": {"palette": "warm", "voice": "direct"},
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == "project-1"
    assert body["style_bible"]["voice"] == "direct"


def test_create_and_fetch_composition_endpoints(client: TestClient) -> None:
    create_response = client.post(
        "/v1/compositions",
        json={
            "project_id": "project-1",
            "prompt": "Explain photosynthesis for kids with visuals.",
            "target_platform": "web",
            "requested_modalities": ["text", "image", "audio"],
            "max_parts": 6,
        },
    )
    assert create_response.status_code == 201
    create_body = create_response.json()
    assert create_body["composition_id"] == "comp-1"
    assert len(create_body["parts"]) == 3

    get_response = client.get("/v1/compositions/comp-1")
    assert get_response.status_code == 200
    assert get_response.json()["composition_id"] == "comp-1"


def test_stream_and_part_regeneration_endpoints(client: TestClient) -> None:
    stream_response = client.get("/v1/compositions/comp-1/stream")
    assert stream_response.status_code == 200
    assert "event: part" in stream_response.text

    patch_response = client.patch(
        "/v1/compositions/comp-1/parts/part-1",
        json={"instruction": "Make this more energetic."},
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["version"] == 2
    assert patched["parts"][0]["content"] == "Make this more energetic."


def test_asset_export_and_usage_endpoints(client: TestClient) -> None:
    asset_response = client.post(
        "/v1/assets:upload-url",
        json={"filename": "cover.png", "mime_type": "image/png"},
    )
    assert asset_response.status_code == 200
    asset_id = asset_response.json()["asset_id"]

    get_asset_response = client.get(f"/v1/assets/{asset_id}")
    assert get_asset_response.status_code == 200
    assert get_asset_response.json()["status"] == "ready"

    export_response = client.post(
        "/v1/compositions/comp-1:export",
        json={"export_format": "zip"},
    )
    assert export_response.status_code == 200
    assert export_response.json()["export_id"] == "export-1"

    usage_response = client.get("/v1/usage")
    assert usage_response.status_code == 200
    assert usage_response.json()["usage"]["prompt_tokens"] == 100

