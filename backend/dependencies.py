from functools import lru_cache

from fastapi import Depends

from config import get_settings
from gemini_story_generator import GeminiStoryGenerator
from state_store import InMemoryStoryStateRepository, StoryStateRepository
from story_service import StoryEngineService

_story_repository = InMemoryStoryStateRepository()


def get_story_repository() -> StoryStateRepository:
    return _story_repository


@lru_cache
def _get_story_generator_singleton() -> GeminiStoryGenerator:
    return GeminiStoryGenerator(settings=get_settings())


def get_story_generator() -> GeminiStoryGenerator:
    return _get_story_generator_singleton()


def get_story_service(
    repository: StoryStateRepository = Depends(get_story_repository),
    generator: GeminiStoryGenerator = Depends(get_story_generator),
) -> StoryEngineService:
    return StoryEngineService(repository=repository, generator=generator)
