from state_store import InMemoryStoryStateRepository, StoryStateRepository

_story_repository = InMemoryStoryStateRepository()


def get_story_repository() -> StoryStateRepository:
    return _story_repository

