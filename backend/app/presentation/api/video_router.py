from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.application.errors import VideoGenerationError, VideoJobNotFoundError
from app.application.use_cases.video_generation import VideoGenerationUseCase
from app.presentation.api.dependencies import get_video_use_case
from app.presentation.api.video_schemas import (
    VideoGenerateRequest,
    VideoJobListResponse,
    VideoJobResponse,
    to_generate_video_command,
    to_video_job_response,
)

video_router = APIRouter(prefix="/v1/videos", tags=["video"])


@video_router.post(
    "/generate",
    response_model=VideoJobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_video(
    request: VideoGenerateRequest,
    use_case: VideoGenerationUseCase = Depends(get_video_use_case),
) -> VideoJobResponse:
    try:
        result = await use_case.generate_video(to_generate_video_command(request))
        return to_video_job_response(result)
    except VideoGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@video_router.get(
    "/{job_id}",
    response_model=VideoJobResponse,
)
async def get_video_job(
    job_id: str,
    use_case: VideoGenerationUseCase = Depends(get_video_use_case),
) -> VideoJobResponse:
    try:
        return to_video_job_response(use_case.get_job(job_id))
    except VideoJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@video_router.get(
    "/{job_id}/download",
)
async def download_video(
    job_id: str,
    use_case: VideoGenerationUseCase = Depends(get_video_use_case),
) -> FileResponse:
    try:
        result = use_case.get_job(job_id)
    except VideoJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if result.status != "completed" or not result.video_uri:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Video not ready (status: {result.status}).",
        )

    return FileResponse(
        path=result.video_uri,
        media_type="video/mp4",
        filename=f"{result.job_id}.mp4",
    )


@video_router.get(
    "",
    response_model=VideoJobListResponse,
)
async def list_video_jobs(
    use_case: VideoGenerationUseCase = Depends(get_video_use_case),
) -> VideoJobListResponse:
    jobs = use_case.list_jobs()
    return VideoJobListResponse(
        jobs=[to_video_job_response(j) for j in jobs],
        total=len(jobs),
    )
