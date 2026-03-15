from functools import lru_cache

from fastapi import Depends

from app.application.ports.story_generator import StoryGeneratorPort
from app.application.use_cases.story_engine import StoryEngineUseCase
from app.core.settings import get_settings
from app.domain.repositories.story_state_repository import StoryStateRepository
from app.infrastructure.repositories.in_memory_story_repository import InMemoryStoryStateRepository

_story_repository = InMemoryStoryStateRepository()


def get_repository() -> StoryStateRepository:
    return _story_repository


@lru_cache
def _get_ai_generator_singleton() -> StoryGeneratorPort:
    from app.infrastructure.ai.gemini_story_generator import GeminiStoryGenerator

    return GeminiStoryGenerator(settings=get_settings())


def get_ai_generator() -> StoryGeneratorPort:
    return _get_ai_generator_singleton()


def get_use_case(
    repository: StoryStateRepository = Depends(get_repository),
    generator: StoryGeneratorPort = Depends(get_ai_generator),
) -> StoryEngineUseCase:
    return StoryEngineUseCase(repository=repository, generator=generator)
