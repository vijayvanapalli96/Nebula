from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from gemini_story_generator import GeminiStoryGenerator
from schemas import (
    HistoryEntry,
    SceneChoice,
    SceneResponse,
    StoryActionRequest,
    StoryActionResponse,
    StoryCard,
    StoryStartRequest,
    StoryStartResponse,
    StoryState,
)
from state_store import StoryStateRepository


class SessionNotFoundError(ValueError):
    pass


class InvalidChoiceError(ValueError):
    pass


class StoryEngineService:
    def __init__(self, repository: StoryStateRepository, generator: GeminiStoryGenerator) -> None:
        self._repository = repository
        self._generator = generator

    def start_story(self, request: StoryStartRequest) -> StoryStartResponse:
        session_id = str(uuid4())
        state = StoryState(
            session_id=session_id,
            genre=request.genre.strip(),
            character_name=request.name.strip(),
            archetype=request.archetype.strip(),
            motivation=request.motivation.strip(),
        )

        scene = self._generator.generate_opening_scene(state)
        self._normalize_scene(scene, chapter=1)
        state.current_scene = scene
        state.history_log.append(
            HistoryEntry(
                turn=1,
                entry_type="scene",
                scene_id=scene.metadata.scene_id,
                content=scene.narrative_text,
            )
        )
        state.updated_at = datetime.utcnow()
        self._repository.create(state)

        return StoryStartResponse(session_id=session_id, scene=scene)

    def apply_action(self, request: StoryActionRequest) -> StoryActionResponse:
        state = self._repository.get(request.session_id)
        if state is None:
            raise SessionNotFoundError(f"Session '{request.session_id}' not found.")
        if state.current_scene is None:
            raise InvalidChoiceError("Current scene is missing for this session.")

        chosen = self._find_choice(
            choices=state.current_scene.choices,
            choice_id=request.choice_id,
        )
        if chosen is None:
            raise InvalidChoiceError(
                f"Choice '{request.choice_id}' is not valid for current scene."
            )

        next_chapter = self._next_chapter(state)
        state.history_log.append(
            HistoryEntry(
                turn=next_chapter,
                entry_type="choice",
                choice_id=chosen.choice_id,
                content=chosen.label,
            )
        )

        scene = self._generator.generate_next_scene(state, chosen=chosen)
        self._normalize_scene(scene, chapter=next_chapter)
        state.current_scene = scene
        state.history_log.append(
            HistoryEntry(
                turn=next_chapter,
                entry_type="scene",
                scene_id=scene.metadata.scene_id,
                content=scene.narrative_text,
            )
        )
        state.updated_at = datetime.utcnow()
        self._repository.save(state)

        return StoryActionResponse(session_id=request.session_id, scene=scene)

    def list_active_stories(self) -> list[StoryCard]:
        sessions = sorted(
            self._repository.list_all(),
            key=lambda item: item.updated_at,
            reverse=True,
        )
        cards: list[StoryCard] = []
        for story in sessions:
            cards.append(
                StoryCard(
                    session_id=story.session_id,
                    title=f"{story.character_name}: {story.genre.title()} Arc",
                    genre=story.genre,
                    character_name=story.character_name,
                    archetype=story.archetype,
                    last_scene_id=(
                        story.current_scene.metadata.scene_id if story.current_scene else None
                    ),
                    updated_at=story.updated_at,
                    choices_available=(
                        len(story.current_scene.choices) if story.current_scene else 0
                    ),
                )
            )
        return cards

    @staticmethod
    def _find_choice(choices: list[SceneChoice], choice_id: str) -> SceneChoice | None:
        for choice in choices:
            if choice.choice_id == choice_id:
                return choice
        return None

    @staticmethod
    def _next_chapter(state: StoryState) -> int:
        scene_entries = [item for item in state.history_log if item.entry_type == "scene"]
        return len(scene_entries) + 1

    @staticmethod
    def _normalize_scene(scene: SceneResponse, chapter: int) -> None:
        scene.metadata.chapter = chapter
        if not scene.metadata.scene_id.strip():
            scene.metadata.scene_id = f"scene-{chapter}"

