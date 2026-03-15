from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.story_commands import ApplyActionCommand, GenerateOpeningSceneCommand, GenerateQuestionsCommand, StartStoryCommand
from app.application.dto.story_results import OpeningSceneResult, QuestionsResult, StoryActionResult, StoryCardView, StoryStartResult
from app.application.errors import InvalidChoiceError, SessionNotFoundError
from app.application.ports.image_storage import ImageStoragePort
from app.application.ports.story_generator import StoryGeneratorPort
from app.application.ports.video_generator import VideoGenerationRequest, VideoGeneratorPort
from app.application.services.media_task_tracker import AssetState, MediaTaskTracker
from app.domain.models.story import HistoryEntry, Scene, SceneChoice, StoryState
from app.domain.repositories.story_state_repository import StoryStateRepository

logger = logging.getLogger(__name__)


class StoryEngineUseCase:
    def __init__(
        self,
        repository: StoryStateRepository,
        generator: StoryGeneratorPort,
        image_storage: ImageStoragePort | None = None,
        video_generator: VideoGeneratorPort | None = None,
        media_tracker: MediaTaskTracker | None = None,
    ) -> None:
        self._repository = repository
        self._generator = generator
        self._image_storage = image_storage
        self._video_generator = video_generator
        self._media_tracker = media_tracker

    async def generate_questions(self, command: GenerateQuestionsCommand) -> QuestionsResult:
        questions = await self._generator.generate_initial_questions(command.theme.strip())
        return QuestionsResult(theme=command.theme.strip(), questions=questions)

    def fire_questions_media(self, questions: list) -> str | None:  # noqa: ANN001
        """Register question-option images as a media request and kick off background generation.

        Returns ``media_request_id`` (or ``None`` if storage is unavailable).
        """
        if self._image_storage is None or self._media_tracker is None:
            return None

        assets: list[AssetState] = []
        for qi, q in enumerate(questions):
            for oi, opt in enumerate(q.options):
                if opt.image_prompt:
                    assets.append(AssetState(
                        asset_key=f"q{qi}_opt{oi}_image",
                        asset_type="image",
                        prompt=opt.image_prompt,
                    ))

        if not assets:
            return None

        request_id = self._media_tracker.create_request(assets)
        asyncio.create_task(self._run_questions_media(request_id, questions))
        return request_id

    async def _run_questions_media(self, request_id: str, questions: list) -> None:  # noqa: ANN001
        """Background coroutine: generate all question-option images in parallel."""

        async def _process(qi: int, oi: int, prompt: str) -> None:
            asset_key = f"q{qi}_opt{oi}_image"
            try:
                image_bytes = await self._generator.generate_option_image(prompt)
                path = f"question-options/{uuid4()}.png"
                uri = await self._image_storage.upload_image(image_bytes, path)  # type: ignore[union-attr]
                self._media_tracker.mark_completed(request_id, asset_key, uri)  # type: ignore[union-attr]
            except Exception as exc:
                self._media_tracker.mark_failed(request_id, asset_key, str(exc))  # type: ignore[union-attr]

        tasks = [
            _process(qi, oi, opt.image_prompt)
            for qi, q in enumerate(questions)
            for oi, opt in enumerate(q.options)
            if opt.image_prompt
        ]
        await asyncio.gather(*tasks)
    async def generate_opening_scene(self, command: GenerateOpeningSceneCommand) -> OpeningSceneResult:
        answers_tuples = [(a.question, a.answer) for a in command.answers]
        scene = await self._generator.generate_opening_scene_from_answers(
            theme=command.theme.strip(),
            character_name=command.character_name.strip(),
            answers=answers_tuples,
        )

        return OpeningSceneResult(
            theme=command.theme.strip(),
            character_name=command.character_name.strip(),
            scene=scene,
        )

    def fire_opening_scene_media(self, scene) -> str | None:  # noqa: ANN001
        """Register opening-scene media as a request and kick off background generation.

        Returns ``media_request_id`` (or ``None`` if storage is unavailable).
        """
        if self._image_storage is None or self._media_tracker is None:
            return None

        assets: list[AssetState] = []

        # Scene-level video
        if scene.video_prompt and self._video_generator is not None:
            assets.append(AssetState(
                asset_key="scene_video",
                asset_type="video",
                prompt=scene.video_prompt,
            ))

        # Per-choice assets
        for choice in scene.choices:
            if choice.image_prompt:
                assets.append(AssetState(
                    asset_key=f"choice_{choice.choice_id}_image",
                    asset_type="image",
                    prompt=choice.image_prompt,
                ))
            if choice.video_prompt and self._video_generator is not None:
                assets.append(AssetState(
                    asset_key=f"choice_{choice.choice_id}_video",
                    asset_type="video",
                    prompt=choice.video_prompt,
                ))

        if not assets:
            return None

        request_id = self._media_tracker.create_request(assets)
        asyncio.create_task(self._run_opening_scene_media(request_id, scene))
        return request_id

    async def _run_opening_scene_media(self, request_id: str, scene) -> None:  # noqa: ANN001
        """Background coroutine: generate all opening-scene media in parallel."""

        async def _gen_image(asset_key: str, prompt: str, path_prefix: str) -> None:
            try:
                image_bytes = await self._generator.generate_option_image(prompt)
                path = f"{path_prefix}/{uuid4()}.png"
                uri = await self._image_storage.upload_image(image_bytes, path)  # type: ignore[union-attr]
                self._media_tracker.mark_completed(request_id, asset_key, uri)  # type: ignore[union-attr]
            except Exception as exc:
                self._media_tracker.mark_failed(request_id, asset_key, str(exc))  # type: ignore[union-attr]

        async def _gen_video(asset_key: str, prompt: str, path_prefix: str) -> None:
            try:
                req = VideoGenerationRequest(
                    prompt=prompt,
                    model="veo-2.0-generate-001",
                    duration_seconds=5,
                    aspect_ratio="16:9",
                )
                result = await self._video_generator.generate(req)  # type: ignore[union-attr]
                path = f"{path_prefix}/{uuid4()}.mp4"
                uri = await self._image_storage.upload_video(result.video_bytes, path)  # type: ignore[union-attr]
                self._media_tracker.mark_completed(request_id, asset_key, uri)  # type: ignore[union-attr]
            except Exception as exc:
                self._media_tracker.mark_failed(request_id, asset_key, str(exc))  # type: ignore[union-attr]

        tasks: list = []

        if scene.video_prompt and self._video_generator is not None:
            tasks.append(_gen_video("scene_video", scene.video_prompt, "opening-scene"))

        for choice in scene.choices:
            if choice.image_prompt:
                tasks.append(_gen_image(
                    f"choice_{choice.choice_id}_image", choice.image_prompt, "choice-images",
                ))
            if choice.video_prompt and self._video_generator is not None:
                tasks.append(_gen_video(
                    f"choice_{choice.choice_id}_video", choice.video_prompt, f"choice-{choice.choice_id}",
                ))

        if tasks:
            await asyncio.gather(*tasks)

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

