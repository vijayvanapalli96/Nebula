import logging
from functools import lru_cache

from fastapi import Depends, Header, HTTPException, status
from firebase_admin import auth as admin_auth

from app.infrastructure.firebase.admin import ensure_initialized

from app.application.ports.image_storage import ImageStoragePort
from app.application.ports.interleaved_generator import InterleavedGeneratorPort
from app.application.ports.story_generator import StoryGeneratorPort
from app.application.ports.video_generator import VideoGeneratorPort
from app.application.services.media_task_tracker import MediaTaskTracker, get_media_tracker
from app.application.use_cases.creative_storytelling import CreativeStorytellingUseCase
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.application.use_cases.video_generation import VideoGenerationUseCase
from app.core.settings import get_settings
from app.domain.repositories.asset_repository import AssetRepository
from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.story_state_repository import StoryStateRepository
from app.domain.repositories.story_theme_repository import StoryThemeRepository
from app.domain.repositories.usage_repository import UsageRepository
from app.domain.repositories.video_repository import VideoJobRepository
from app.infrastructure.repositories.firestore_story_theme_repository import FirestoreStoryThemeRepository
from app.infrastructure.repositories.in_memory_creative_repository import (
    InMemoryAssetRepository,
    InMemoryCompositionRepository,
    InMemoryCreativeWorkspaceRepository,
    InMemoryProjectRepository,
    InMemoryUsageRepository,
)
from app.infrastructure.repositories.in_memory_story_repository import InMemoryStoryStateRepository
from app.infrastructure.repositories.in_memory_story_theme_repository import InMemoryStoryThemeRepository
from app.infrastructure.repositories.in_memory_video_repository import InMemoryVideoJobRepository

_story_repository = InMemoryStoryStateRepository()
_video_repository = InMemoryVideoJobRepository()
_theme_repository = InMemoryStoryThemeRepository()
_creative_workspace = InMemoryCreativeWorkspaceRepository()
_project_repository = InMemoryProjectRepository(_creative_workspace)
_composition_repository = InMemoryCompositionRepository(_creative_workspace)
_asset_repository = InMemoryAssetRepository(_creative_workspace)
_usage_repository = InMemoryUsageRepository(_creative_workspace)


def get_repository() -> StoryStateRepository:
    return _story_repository


@lru_cache
def _get_ai_generator_singleton() -> StoryGeneratorPort:
    from app.infrastructure.ai.gemini_story_generator import GeminiStoryGenerator

    return GeminiStoryGenerator(settings=get_settings())


def get_ai_generator() -> StoryGeneratorPort:
    return _get_ai_generator_singleton()


@lru_cache
def _get_image_storage_singleton() -> ImageStoragePort | None:
    settings = get_settings()
    if not settings.gcs_bucket_name:
        return None
    from app.infrastructure.storage.gcs_image_storage import GcsImageStorage

    return GcsImageStorage(settings=settings)


def get_image_storage() -> ImageStoragePort | None:
    return _get_image_storage_singleton()


@lru_cache
def _get_video_generator_singleton() -> VideoGeneratorPort:
    from app.infrastructure.ai.gemini_video_generator import GeminiVideoGenerator

    return GeminiVideoGenerator(settings=get_settings())


def get_video_generator() -> VideoGeneratorPort:
    return _get_video_generator_singleton()


@lru_cache
def _get_firestore_client_singleton() -> object | None:
    settings = get_settings()
    project_id = settings.firebase_project_id.strip()
    credentials_path = settings.firebase_credentials_path.strip()
    if not project_id and not credentials_path:
        return None

    try:
        from google.cloud import firestore
        if credentials_path:
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
            )
            resolved_project_id = project_id or credentials.project_id
            if not resolved_project_id:
                raise ValueError(
                    "FIREBASE_PROJECT_ID is not set and project_id is missing in "
                    "FIREBASE_CREDENTIALS_PATH.",
                )
            return firestore.Client(
                project=resolved_project_id,
                credentials=credentials,
            )

        return firestore.Client(project=project_id)
    except Exception as exc:  # pragma: no cover - defensive runtime fallback
        logging.getLogger(__name__).warning(
            "Falling back to in-memory themes repository. Firestore client init failed: %s",
            exc,
        )
        return None


@lru_cache
def _get_story_theme_repository_singleton() -> StoryThemeRepository:
    settings = get_settings()
    firestore_client = _get_firestore_client_singleton()
    collection_name = settings.firebase_themes_collection.strip()

    if firestore_client is not None and collection_name:
        return FirestoreStoryThemeRepository(
            firestore_client=firestore_client,
            collection_name=collection_name,
        )
    return _theme_repository


def get_story_theme_repository() -> StoryThemeRepository:
    return _get_story_theme_repository_singleton()


def get_use_case(
    repository: StoryStateRepository = Depends(get_repository),
    generator: StoryGeneratorPort = Depends(get_ai_generator),
    image_storage: ImageStoragePort | None = Depends(get_image_storage),
    video_generator: VideoGeneratorPort = Depends(get_video_generator),
    theme_repository: StoryThemeRepository = Depends(get_story_theme_repository),
) -> StoryEngineUseCase:
    return StoryEngineUseCase(
        repository=repository,
        generator=generator,
        image_storage=image_storage,
        video_generator=video_generator,
        theme_repository=theme_repository,
        media_tracker=get_media_tracker(),
    )


def get_project_repository() -> ProjectRepository:
    return _project_repository


def get_composition_repository() -> CompositionRepository:
    return _composition_repository


def get_asset_repository() -> AssetRepository:
    return _asset_repository


def get_usage_repository() -> UsageRepository:
    return _usage_repository


@lru_cache
def _get_interleaved_generator_singleton() -> InterleavedGeneratorPort:
    from app.infrastructure.ai.gemini_interleaved_generator import GeminiInterleavedGenerator

    return GeminiInterleavedGenerator(settings=get_settings())


def get_interleaved_generator() -> InterleavedGeneratorPort:
    return _get_interleaved_generator_singleton()


def get_creative_use_case(
    project_repository: ProjectRepository = Depends(get_project_repository),
    composition_repository: CompositionRepository = Depends(get_composition_repository),
    asset_repository: AssetRepository = Depends(get_asset_repository),
    usage_repository: UsageRepository = Depends(get_usage_repository),
    generator: InterleavedGeneratorPort = Depends(get_interleaved_generator),
) -> CreativeStorytellingUseCase:
    return CreativeStorytellingUseCase(
        project_repository=project_repository,
        composition_repository=composition_repository,
        asset_repository=asset_repository,
        usage_repository=usage_repository,
        generator=generator,
    )


def get_video_repository() -> VideoJobRepository:
    return _video_repository


def get_video_use_case(
    repository: VideoJobRepository = Depends(get_video_repository),
    generator: VideoGeneratorPort = Depends(get_video_generator),
) -> VideoGenerationUseCase:
    return VideoGenerationUseCase(repository=repository, generator=generator)


# ── Shared Firebase auth guard ────────────────────────────────────────────────


async def require_auth(authorization: str = Header(default="")) -> str:
    """
    FastAPI dependency — verifies the Firebase ID-token in the
    ``Authorization: Bearer <token>`` header.

    Returns the caller's UID on success.
    Raises HTTP 401 on a missing or invalid token.
    Add to any route or ``APIRouter`` that must be authenticated:

        @router.get("/example", dependencies=[Depends(require_auth)])
        # or at router level:
        APIRouter(dependencies=[Depends(require_auth)])
    """
    # Ensure Firebase Admin app is initialised before calling verify_id_token.
    # Wrapped in try/except so any credential/init failure returns a clean 503
    # rather than an unhandled exception (which Cloud Run logs as 502).
    try:
        ensure_initialized()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unavailable: {exc}",
        ) from exc

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    id_token = authorization[7:]
    try:
        decoded = admin_auth.verify_id_token(id_token)
        return decoded["uid"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
