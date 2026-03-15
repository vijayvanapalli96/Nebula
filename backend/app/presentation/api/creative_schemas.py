from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.application.dto.creative_commands import (
    CreateAssetUploadCommand,
    CreateCompositionCommand,
    CreateProjectCommand,
    ExportCompositionCommand,
    RegenerateCompositionPartCommand,
)
from app.application.dto.creative_results import ExportResult
from app.domain.models.composition import AssetRecord, Composition, CompositionPart, GenerationUsage, Project


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    use_case: str = Field(..., min_length=1)
    tone: str | None = None
    style_bible: dict[str, Any] = Field(default_factory=dict)


class ProjectResponse(BaseModel):
    project_id: str
    title: str
    use_case: str
    tone: str | None = None
    style_bible: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class CompositionCreateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    target_platform: str = Field(default="web", min_length=1)
    project_id: str | None = None
    requested_modalities: list[
        Literal["text", "image", "audio", "video", "caption", "cta"]
    ] = Field(default_factory=lambda: ["text", "image"])
    max_parts: int = Field(default=8, ge=1, le=20)


class CompositionPartResponse(BaseModel):
    part_id: str
    type: Literal["text", "image", "audio", "video", "caption", "cta"]
    sequence: int
    status: Literal["queued", "generating", "completed", "failed"]
    content: str | None = None
    asset_uri: str | None = None
    mime_type: str | None = None
    duration_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class UsageResponse(BaseModel):
    prompt_tokens: int
    output_tokens: int
    image_count: int
    audio_seconds: int
    video_seconds: int


class CompositionResponse(BaseModel):
    composition_id: str
    project_id: str | None = None
    prompt: str
    target_platform: str
    status: Literal["queued", "generating", "partial", "completed", "failed"]
    requested_modalities: list[Literal["text", "image", "audio", "video", "caption", "cta"]]
    parts: list[CompositionPartResponse]
    version: int
    usage: UsageResponse
    created_at: datetime
    updated_at: datetime


class PartRegenerateRequest(BaseModel):
    instruction: str | None = None


class AssetUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    mime_type: str = Field(..., min_length=1)
    expires_in_minutes: int = Field(default=30, ge=1, le=240)


class AssetResponse(BaseModel):
    asset_id: str
    filename: str
    mime_type: str
    upload_url: str
    storage_uri: str
    expires_at: datetime
    status: Literal["pending_upload", "ready", "failed"]
    created_at: datetime
    updated_at: datetime


class ExportRequest(BaseModel):
    export_format: str = Field(default="json", min_length=1)


class ExportResponse(BaseModel):
    export_id: str
    composition_id: str
    export_format: str
    download_url: str
    expires_at: datetime


class UsageSnapshotResponse(BaseModel):
    usage: UsageResponse


def to_create_project_command(request: ProjectCreateRequest) -> CreateProjectCommand:
    return CreateProjectCommand(
        title=request.title,
        use_case=request.use_case,
        tone=request.tone,
        style_bible=request.style_bible,
    )


def to_create_composition_command(request: CompositionCreateRequest) -> CreateCompositionCommand:
    return CreateCompositionCommand(
        prompt=request.prompt,
        target_platform=request.target_platform,
        project_id=request.project_id,
        requested_modalities=request.requested_modalities,
        max_parts=request.max_parts,
    )


def to_regenerate_part_command(
    composition_id: str,
    part_id: str,
    request: PartRegenerateRequest,
) -> RegenerateCompositionPartCommand:
    return RegenerateCompositionPartCommand(
        composition_id=composition_id,
        part_id=part_id,
        instruction=request.instruction,
    )


def to_asset_upload_command(request: AssetUploadRequest) -> CreateAssetUploadCommand:
    return CreateAssetUploadCommand(
        filename=request.filename,
        mime_type=request.mime_type,
        expires_in_minutes=request.expires_in_minutes,
    )


def to_export_command(
    composition_id: str,
    request: ExportRequest,
) -> ExportCompositionCommand:
    return ExportCompositionCommand(
        composition_id=composition_id,
        export_format=request.export_format,
    )


def to_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        project_id=project.project_id,
        title=project.title,
        use_case=project.use_case,
        tone=project.tone,
        style_bible=project.style_bible,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def to_composition_response(composition: Composition) -> CompositionResponse:
    return CompositionResponse(
        composition_id=composition.composition_id,
        project_id=composition.project_id,
        prompt=composition.prompt,
        target_platform=composition.target_platform,
        status=composition.status,
        requested_modalities=composition.requested_modalities,
        parts=[to_part_response(part) for part in composition.parts],
        version=composition.version,
        usage=to_usage_response(composition.usage),
        created_at=composition.created_at,
        updated_at=composition.updated_at,
    )


def to_part_response(part: CompositionPart) -> CompositionPartResponse:
    return CompositionPartResponse(
        part_id=part.part_id,
        type=part.type,
        sequence=part.sequence,
        status=part.status,
        content=part.content,
        asset_uri=part.asset_uri,
        mime_type=part.mime_type,
        duration_ms=part.duration_ms,
        metadata=part.metadata,
        created_at=part.created_at,
        updated_at=part.updated_at,
    )


def to_asset_response(asset: AssetRecord) -> AssetResponse:
    return AssetResponse(
        asset_id=asset.asset_id,
        filename=asset.filename,
        mime_type=asset.mime_type,
        upload_url=asset.upload_url,
        storage_uri=asset.storage_uri,
        expires_at=asset.expires_at,
        status=asset.status,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


def to_export_response(result: ExportResult) -> ExportResponse:
    return ExportResponse(
        export_id=result.export_id,
        composition_id=result.composition_id,
        export_format=result.export_format,
        download_url=result.download_url,
        expires_at=result.expires_at,
    )


def to_usage_snapshot_response(usage: GenerationUsage) -> UsageSnapshotResponse:
    return UsageSnapshotResponse(usage=to_usage_response(usage))


def to_usage_response(usage: GenerationUsage) -> UsageResponse:
    return UsageResponse(
        prompt_tokens=usage.prompt_tokens,
        output_tokens=usage.output_tokens,
        image_count=usage.image_count,
        audio_seconds=usage.audio_seconds,
        video_seconds=usage.video_seconds,
    )

