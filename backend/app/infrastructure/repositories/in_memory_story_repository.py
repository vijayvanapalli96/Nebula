from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock

from app.domain.models.story import StoryState
from app.domain.repositories.story_state_repository import StoryStateRepository


class InMemoryStoryStateRepository(StoryStateRepository):
    """
    Redis-ready repository surface:
    methods map cleanly to common redis hash/list operations.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, StoryState] = {}
        self._lock = RLock()

    def create(self, state: StoryState) -> None:
        with self._lock:
            self._sessions[state.session_id] = deepcopy(state)

    def get(self, session_id: str) -> StoryState | None:
        with self._lock:
            state = self._sessions.get(session_id)
            return deepcopy(state) if state is not None else None

    def save(self, state: StoryState) -> None:
        with self._lock:
            state.updated_at = datetime.now(UTC)
            self._sessions[state.session_id] = deepcopy(state)

    def list_all(self) -> list[StoryState]:
        with self._lock:
            return [deepcopy(story) for story in self._sessions.values()]

