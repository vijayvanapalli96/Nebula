from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.story_commands import ApplyActionCommand, StartStoryCommand
from app.application.dto.story_results import StoryActionResult, StoryCardView, StoryStartResult
from app.application.errors import InvalidChoiceError, SessionNotFoundError
from app.application.ports.story_generator import StoryGeneratorPort
from app.domain.models.story import HistoryEntry, Scene, SceneChoice, StoryState
from app.domain.repositories.story_state_repository import StoryStateRepository


class StoryEngineUseCase:
    def __init__(self, repository: StoryStateRepository, generator: StoryGeneratorPort) -> None:
        self._repository = repository
        self._generator = generator

    async def start_story(self, command: StartStoryCommand) -> StoryStartResult:
        state = StoryState(
            session_id=str(uuid4()),
            genre=command.genre.strip(),
            character_name=command.name.strip(),
            archetype=command.archetype.strip(),
            motivation=command.motivation.strip(),
        )

        scene = await self._generator.generate_opening_scene(state)
        self._normalize_scene(scene=scene, chapter=1)
        state.current_scene = scene
        state.history_log.append(
            HistoryEntry(
                turn=1,
                entry_type="scene",
                scene_id=scene.metadata.scene_id,
                content=scene.narrative_text,
            )
        )
        state.updated_at = datetime.now(UTC)
        self._repository.create(state)

        return StoryStartResult(session_id=state.session_id, scene=scene)

    async def apply_action(self, command: ApplyActionCommand) -> StoryActionResult:
        state = self._repository.get(command.session_id)
        if state is None:
            raise SessionNotFoundError(f"Session '{command.session_id}' not found.")
        if state.current_scene is None:
            raise InvalidChoiceError("Current scene is missing for this session.")

        chosen = self._find_choice(
            choices=state.current_scene.choices,
            choice_id=command.choice_id,
        )
        if chosen is None:
            raise InvalidChoiceError(
                f"Choice '{command.choice_id}' is not valid for current scene."
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

        scene = await self._generator.generate_next_scene(state=state, chosen=chosen)
        self._normalize_scene(scene=scene, chapter=next_chapter)
        state.current_scene = scene
        state.history_log.append(
            HistoryEntry(
                turn=next_chapter,
                entry_type="scene",
                scene_id=scene.metadata.scene_id,
                content=scene.narrative_text,
            )
        )
        state.updated_at = datetime.now(UTC)
        self._repository.save(state)

        return StoryActionResult(session_id=state.session_id, scene=scene)

    def list_active_stories(self) -> list[StoryCardView]:
        sessions = sorted(
            self._repository.list_all(),
            key=lambda item: item.updated_at,
            reverse=True,
        )
        return [self._to_story_card_view(state=story) for story in sessions]

    @staticmethod
    def _to_story_card_view(state: StoryState) -> StoryCardView:
        return StoryCardView(
            session_id=state.session_id,
            title=f"{state.character_name}: {state.genre.title()} Arc",
            genre=state.genre,
            character_name=state.character_name,
            archetype=state.archetype,
            last_scene_id=state.current_scene.metadata.scene_id if state.current_scene else None,
            updated_at=state.updated_at,
            choices_available=len(state.current_scene.choices) if state.current_scene else 0,
        )

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
    def _normalize_scene(scene: Scene, chapter: int) -> None:
        scene.metadata.chapter = chapter
        if not scene.metadata.scene_id.strip():
            scene.metadata.scene_id = f"scene-{chapter}"

