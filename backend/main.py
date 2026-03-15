from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from dependencies import get_story_service
from gemini_story_generator import StoryGenerationError
from schemas import (
    StoryActionRequest,
    StoryActionResponse,
    StoryCard,
    StoryStartRequest,
    StoryStartResponse,
)
from story_service import InvalidChoiceError, SessionNotFoundError, StoryEngineService

settings = get_settings()
app = FastAPI(title=settings.app_name)

allow_origins = (
    ["*"]
    if settings.cors_allow_origins.strip() == "*"
    else [item.strip() for item in settings.cors_allow_origins.split(",") if item.strip()]
)
allow_credentials = settings.cors_allow_origins.strip() != "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.post(
    "/story/start",
    response_model=StoryStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_story(
    request: StoryStartRequest,
    service: StoryEngineService = Depends(get_story_service),
) -> StoryStartResponse:
    try:
        return await service.start_story(request)
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.post("/story/action", response_model=StoryActionResponse)
async def story_action(
    request: StoryActionRequest,
    service: StoryEngineService = Depends(get_story_service),
) -> StoryActionResponse:
    try:
        return await service.apply_action(request)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidChoiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@app.get("/stories/me", response_model=list[StoryCard])
async def list_my_stories(
    service: StoryEngineService = Depends(get_story_service),
) -> list[StoryCard]:
    return service.list_active_stories()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
