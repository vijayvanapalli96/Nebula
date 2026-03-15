from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.application.errors import (
    AssetNotFoundError,
    CompositionNotFoundError,
    PartNotFoundError,
    ProjectNotFoundError,
    StoryGenerationError,
)
from app.application.use_cases.creative_storytelling import CreativeStorytellingUseCase
from app.presentation.api.creative_schemas import (
    AssetResponse,
    AssetUploadRequest,
    CompositionCreateRequest,
    CompositionResponse,
    ExportRequest,
    ExportResponse,
    PartRegenerateRequest,
    ProjectCreateRequest,
    ProjectResponse,
    UsageSnapshotResponse,
    to_asset_response,
    to_asset_upload_command,
    to_composition_response,
    to_create_composition_command,
    to_create_project_command,
    to_export_command,
    to_export_response,
    to_project_response,
    to_regenerate_part_command,
    to_usage_snapshot_response,
)
from app.presentation.api.dependencies import get_creative_use_case

creative_router = APIRouter(prefix="/v1", tags=["creative"])


@creative_router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    request: ProjectCreateRequest,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> ProjectResponse:
    project = use_case.create_project(to_create_project_command(request))
    return to_project_response(project)


@creative_router.post(
    "/compositions",
    response_model=CompositionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_composition(
    request: CompositionCreateRequest,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> CompositionResponse:
    try:
        composition = await use_case.create_composition(to_create_composition_command(request))
        return to_composition_response(composition)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except StoryGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@creative_router.get("/compositions/{composition_id}", response_model=CompositionResponse)
async def get_composition(
    composition_id: str,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> CompositionResponse:
    try:
        return to_composition_response(use_case.get_composition(composition_id))
    except CompositionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@creative_router.get("/compositions/{composition_id}/stream")
async def stream_composition(
    composition_id: str,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> StreamingResponse:
    try:
        events = use_case.build_stream_events(composition_id)
    except CompositionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    async def event_stream() -> str:
        for event in events:
            yield f"event: {event['event']}\ndata: {event['data']}\n\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@creative_router.patch(
    "/compositions/{composition_id}/parts/{part_id}",
    response_model=CompositionResponse,
)
async def regenerate_composition_part(
    composition_id: str,
    part_id: str,
    request: PartRegenerateRequest,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> CompositionResponse:
    try:
        composition = await use_case.regenerate_part(
            to_regenerate_part_command(composition_id=composition_id, part_id=part_id, request=request)
        )
        return to_composition_response(composition)
    except CompositionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PartNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except StoryGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@creative_router.post("/assets:upload-url", response_model=AssetResponse)
async def create_asset_upload_url(
    request: AssetUploadRequest,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> AssetResponse:
    asset = use_case.create_asset_upload(to_asset_upload_command(request))
    return to_asset_response(asset)


@creative_router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> AssetResponse:
    try:
        return to_asset_response(use_case.get_asset(asset_id))
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@creative_router.post("/compositions/{composition_id}:export", response_model=ExportResponse)
async def export_composition(
    composition_id: str,
    request: ExportRequest,
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> ExportResponse:
    try:
        result = use_case.export_composition(to_export_command(composition_id, request))
        return to_export_response(result)
    except CompositionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@creative_router.get("/usage", response_model=UsageSnapshotResponse)
async def get_usage_snapshot(
    use_case: CreativeStorytellingUseCase = Depends(get_creative_use_case),
) -> UsageSnapshotResponse:
    return to_usage_snapshot_response(use_case.get_usage())

