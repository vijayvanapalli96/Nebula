from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from typing import Protocol

from schemas import StoryState


class StoryStateRepository(Protocol):
    def create(self, state: StoryState) -> None:
        ...

    def get(self, session_id: str) -> StoryState | None:
        ...

    def save(self, state: StoryState) -> None:
        ...

    def list_all(self) -> list[StoryState]:
        ...


class InMemoryStoryStateRepository:
    """
    Redis-ready repository surface:
    methods map cleanly to common redis hash/list operations.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, StoryState] = {}
        self._lock = RLock()

    def create(self, state: StoryState) -> None:
        with self._lock:
            self._sessions[state.session_id] = state.model_copy(deep=True)

    def get(self, session_id: str) -> StoryState | None:
        with self._lock:
            state = self._sessions.get(session_id)
            if state is None:
                return None
            return state.model_copy(deep=True)

    def save(self, state: StoryState) -> None:
        with self._lock:
            state.updated_at = datetime.now(UTC)
            self._sessions[state.session_id] = state.model_copy(deep=True)

    def list_all(self) -> list[StoryState]:
        with self._lock:
            return [story.model_copy(deep=True) for story in self._sessions.values()]
