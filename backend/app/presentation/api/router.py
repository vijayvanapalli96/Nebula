from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.errors import InvalidChoiceError, SessionNotFoundError, StoryGenerationError
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.core.settings import get_settings
from app.presentation.api.dependencies import get_use_case
from app.presentation.api.schemas import (
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    StoryActionRequest,
    StoryActionResponse,
    StoryCardResponse,
    StoryStartRequest,
    StoryStartResponse,
    to_action_command,
    to_action_response,
    to_questions_command,
    to_questions_response,
    to_start_command,
    to_start_response,
    to_story_card_response,
)

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": get_settings().app_env}


@router.post(
    "/story/questions",
    response_model=GenerateQuestionsResponse,
    status_code=status.HTTP_200_OK,
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
    "/story/start",
    response_model=StoryStartResponse,
    status_code=status.HTTP_201_CREATED,
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


@router.post("/story/action", response_model=StoryActionResponse)
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
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> list[StoryCardResponse]:
    views = use_case.list_active_stories()
    return [to_story_card_response(item) for item in views]
