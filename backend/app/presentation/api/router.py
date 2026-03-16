from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.errors import InvalidChoiceError, SessionNotFoundError, StoryGenerationError
from app.application.services.media_task_tracker import MediaTaskTracker, get_media_tracker
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.core.settings import get_settings
from app.presentation.api.dependencies import get_use_case, require_auth
from app.presentation.api.schemas import (
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    MediaResponse,
    OpeningSceneRequest,
    OpeningSceneResponse,
    StoryActionRequest,
    StoryActionResponse,
    StoryCardResponse,
    StorySceneResponse,
    StoryStartRequest,
    StoryStartResponse,
    StoryThemeResponse,
    to_action_command,
    to_action_response,
    to_opening_scene_command,
    to_opening_scene_response,
    to_questions_command,
    to_questions_response,
    to_start_command,
    to_start_response,
    to_story_card_response,
    to_story_scene_response,
    to_story_theme_response,
)

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": get_settings().app_env}


@router.post(
    "/story/questions",
    response_model=GenerateQuestionsResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_auth)],
)
async def generate_questions(
    request: GenerateQuestionsRequest,
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> GenerateQuestionsResponse:
    try:
        result = await use_case.generate_questions(to_questions_command(request))
        return to_questions_response(result)
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post(
    "/story/opening",
    response_model=OpeningSceneResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_auth)],
)
async def generate_opening_scene(
    request: OpeningSceneRequest,
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> OpeningSceneResponse:
    try:
        result = await use_case.generate_opening_scene(to_opening_scene_command(request))
        media_request_id = use_case.fire_opening_scene_media(result.scene)
        return to_opening_scene_response(result, media_request_id=media_request_id)
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get(
    "/story/media/{media_request_id}",
    response_model=MediaResponse,
    status_code=status.HTTP_200_OK,
)
async def get_media(
    media_request_id: str,
    tracker: MediaTaskTracker = Depends(get_media_tracker),
) -> MediaResponse:
    """Return generated media URIs for a request. null values mean still generating."""
    result = tracker.get_status(media_request_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media request '{media_request_id}' not found",
        )
    # Flatten to simple {asset_key: uri_or_null}
    assets = {k: v.get("uri") for k, v in result["assets"].items()}
    return MediaResponse(request_id=media_request_id, assets=assets)


@router.post(
    "/story/start",
    response_model=StoryStartResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_auth)],
)
async def start_story(
    request: StoryStartRequest,
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> StoryStartResponse:
    try:
        result = await use_case.start_story(to_start_command(request))
        return to_start_response(result)
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/story/action", response_model=StoryActionResponse, dependencies=[Depends(require_auth)])
async def story_action(
    request: StoryActionRequest,
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> StoryActionResponse:
    try:
        result = await use_case.apply_action(to_action_command(request))
        return to_action_response(result)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidChoiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/stories/me", response_model=list[StoryCardResponse])
async def list_my_stories(
    user_id: str = Depends(require_auth),
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> list[StoryCardResponse]:
    views = use_case.list_active_stories(user_id=user_id)
    return [to_story_card_response(item) for item in views]


@router.get("/story/themes", response_model=list[StoryThemeResponse])
async def list_story_themes(
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> list[StoryThemeResponse]:
    views = use_case.list_story_themes()
    return [to_story_theme_response(item) for item in views]


@router.get(
    "/stories/{storyId}/scenes",
    response_model=list[StorySceneResponse],
    dependencies=[Depends(require_auth)],
)
async def list_story_scenes(
    storyId: str,
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> list[StorySceneResponse]:
    views = use_case.list_story_scenes(story_id=storyId)
    return [to_story_scene_response(item) for item in views]
