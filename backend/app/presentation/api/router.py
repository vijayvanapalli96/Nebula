from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.errors import InvalidChoiceError, SessionNotFoundError, StoryGenerationError, ThemeNotFoundError
from app.application.ports.image_storage import ImageStoragePort
from app.application.ports.story_generator import StoryGeneratorPort
from app.application.use_cases.generate_story_questions import GenerateStoryQuestionsUseCase
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.core.settings import get_settings
from app.domain.repositories.story_theme_repository import StoryThemeRepository
from app.presentation.api.dependencies import (
    get_ai_generator,
    get_generate_story_questions_use_case,
    get_image_storage,
    get_story_theme_repository,
    get_use_case,
    require_auth,
)
from app.presentation.api.schemas import (
    ChoiceMediaItem,
    GenerateQuestionsResponse,
    GenerateStoryQuestionsRequest,
    OpeningSceneRequest,
    OpeningSceneResponse,
    SceneMediaResponse,
    StoryActionRequest,
    StoryActionResponse,
    StoryCardResponse,
    StoryDetailResponse,
    StorySceneResponse,
    StoryStartRequest,
    StoryStartResponse,
    StoryThemeResponse,
    to_action_command,
    to_action_response,
    to_opening_scene_command,
    to_opening_scene_response,
    to_start_command,
    to_start_response,
    to_story_card_response,
    to_story_detail_response,
    to_story_scene_response,
    to_story_questions_response,
    to_story_theme_response,
)

# ── helpers ───────────────────────────────────────────────────────────────────

async def _normalize_media_urls(view: Any, storage: Any) -> None:
    """Convert raw GCS object paths to signed URLs in-place on view.scenes/questions.

    Also strips the redundant 'gcsPath' field from question options.
    Paths that already begin with https:// are left unchanged.
    """
    targets: list[tuple[dict, str]] = []

    for scene in view.scenes:
        for choice in scene.get("choices", []):
            for key in ("imageUrl", "videoUrl"):
                val = choice.get(key)
                if val and not str(val).startswith("http"):
                    targets.append((choice, key))

    for question in view.questions:
        for option in question.get("options", []):
            option.pop("gcsPath", None)  # remove redundant field
            val = option.get("imageUrl")
            if val and not str(val).startswith("http"):
                targets.append((option, "imageUrl"))

    if not targets:
        return

    signed = await asyncio.gather(*(storage.url_for(t[0][t[1]]) for t in targets))
    for (container, key), url in zip(targets, signed):
        container[key] = url


router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": get_settings().app_env}


@router.post(
    "/story/questions",
    response_model=GenerateQuestionsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_questions(
    request: GenerateStoryQuestionsRequest,
    user_id: str = Depends(require_auth),
    use_case: GenerateStoryQuestionsUseCase = Depends(get_generate_story_questions_use_case),
) -> GenerateQuestionsResponse:
    """
    Full story-question pipeline:
      1. Verify Firebase token → extract user UID
      2. Fetch theme from Firestore by theme_id
      3. Create story document (status = "initializing")
      4. Generate 4 questions via Gemini LLM
      5. Generate per-option images & upload to GCS
      6. Persist questions under users/{uid}/stories/{story_id}/questions/
      7. Update story status → "questions_generated"
      8. Return questions with story_id to the client
    """
    try:
        result = await use_case.execute(user_id=user_id, theme_id=request.theme_id)
        return to_story_questions_response(result)
    except ThemeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post(
    "/story/opening",
    response_model=OpeningSceneResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_opening_scene(
    request: OpeningSceneRequest,
    user_id: str = Depends(require_auth),
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> OpeningSceneResponse:
    if not request.story_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="story_id is required. Make sure /story/questions completed successfully before calling /story/opening.",
        )
    if not request.theme_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="theme_id is required.",
        )
    try:
        result = await use_case.generate_opening_scene(
            command=to_opening_scene_command(request),
            user_id=user_id,
        )
        use_case.fire_opening_scene_media(
            result.scene,
            story_id=result.story_id,
            user_id=user_id,
        )
        return to_opening_scene_response(result)
    except StoryGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get(
    "/story/media/{story_id}/{scene_id}",
    response_model=SceneMediaResponse,
    status_code=status.HTTP_200_OK,
)
async def get_scene_media(
    story_id: str,
    scene_id: str,
    user_id: str = Depends(require_auth),
    use_case: StoryEngineUseCase = Depends(get_use_case),
) -> SceneMediaResponse:
    """Return current image/video GCS paths for all choices in a scene (live from Firestore)."""
    choices = use_case.get_scene_choice_media(
        user_id=user_id,
        story_id=story_id,
        scene_id=scene_id,
    )
    if choices is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene '{scene_id}' not found for story '{story_id}'.",
        )
    return SceneMediaResponse(
        story_id=story_id,
        scene_id=scene_id,
        choices=[
            ChoiceMediaItem(
                choice_id=c["choice_id"],
                image_url=c.get("image_url"),
                video_url=c.get("video_url"),
            )
            for c in choices
        ],
    )


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


@router.get("/story/{user_id}/{story_id}", response_model=StoryDetailResponse)
async def get_story_detail(
    user_id: str,
    story_id: str,
    token_uid: str = Depends(require_auth),
    use_case: StoryEngineUseCase = Depends(get_use_case),
    image_storage: ImageStoragePort | None = Depends(get_image_storage),
) -> StoryDetailResponse:
    if token_uid != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token UID does not match requested user_id.",
        )

    view = use_case.get_story_detail(user_id=user_id, story_id=story_id)
    if view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story '{story_id}' not found for user '{user_id}'.",
        )
    # Convert any raw GCS paths to signed URLs before serialising the response
    if image_storage is not None:
        await _normalize_media_urls(view, image_storage)
    return to_story_detail_response(view)


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


@router.post("/story/themes/generate-thumbnails", status_code=status.HTTP_200_OK)
async def generate_theme_thumbnails(
    theme_repo: StoryThemeRepository = Depends(get_story_theme_repository),
    generator: StoryGeneratorPort = Depends(get_ai_generator),
    image_storage: ImageStoragePort | None = Depends(get_image_storage),
) -> dict:
    """Generate Imagen thumbnails for all active themes, upload to GCS, persist URLs."""
    import asyncio
    import logging
    from uuid import uuid4

    log = logging.getLogger(__name__)

    if image_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GCS image storage is not configured.",
        )

    themes = theme_repo.list_active()
    results: dict[str, str | None] = {}

    async def _gen_thumbnail(theme) -> None:  # noqa: ANN001
        prompt = (
            f"A cinematic, atmospheric movie-poster-style thumbnail for a story genre called "
            f"'{theme.title}'. {theme.tagline} {theme.description.replace(chr(10), ' ')} "
            f"High detail, dramatic lighting, concept art, 16:9 aspect ratio, no text."
        )
        try:
            image_bytes = await generator.generate_option_image(prompt)
            path = f"theme-thumbnails/{theme.theme_id}.png"
            uri = await image_storage.upload_image(image_bytes, path)
            theme_repo.update_image(theme.theme_id, uri)
            results[theme.theme_id] = uri
            log.info("Generated thumbnail for theme %s", theme.theme_id)
        except Exception:
            log.exception("Failed to generate thumbnail for theme %s", theme.theme_id)
            results[theme.theme_id] = None

    await asyncio.gather(*[_gen_thumbnail(t) for t in themes])

    return {
        "generated": sum(1 for v in results.values() if v),
        "failed": sum(1 for v in results.values() if v is None),
        "themes": results,
    }
