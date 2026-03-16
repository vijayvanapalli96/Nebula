from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.story_commands import ApplyActionCommand, GenerateOpeningSceneCommand, GenerateQuestionsCommand, StartStoryCommand
from app.application.dto.story_results import (
    OpeningSceneResult,
    QuestionsResult,
    StoryActionResult,
    StoryCardView,
    StoryDetailView,
    StorySceneAssetRefsView,
    StorySceneGenerationStatusView,
    StorySceneLocationView,
    StorySceneView,
    StoryStartResult,
    StoryThemeView,
)
from app.application.errors import InvalidChoiceError, SessionNotFoundError
from app.application.ports.image_storage import ImageStoragePort
from app.application.ports.story_generator import StoryGeneratorPort
from app.application.ports.video_generator import VideoGenerationRequest, VideoGeneratorPort
from app.application.services.media_task_tracker import AssetState, MediaTaskTracker
from app.domain.models.story import HistoryEntry, Scene, SceneChoice, StoryState
from app.domain.repositories.story_document_repository import StoryDocumentRepository
from app.domain.models.story import HistoryEntry, Scene, SceneChoice, StoryState, UserStoryRecord
from app.domain.repositories.story_scene_repository import StorySceneRepository
from app.domain.repositories.story_state_repository import StoryStateRepository
from app.domain.repositories.story_theme_repository import StoryThemeRepository
from app.domain.repositories.user_story_repository import UserStoryRepository

logger = logging.getLogger(__name__)


class StoryEngineUseCase:
    def __init__(
        self,
        repository: StoryStateRepository,
        generator: StoryGeneratorPort,
        image_storage: ImageStoragePort | None = None,
        video_generator: VideoGeneratorPort | None = None,
        theme_repository: StoryThemeRepository | None = None,
        scene_repository: StorySceneRepository | None = None,
        user_story_repository: UserStoryRepository | None = None,
        media_tracker: MediaTaskTracker | None = None,
        story_doc_repository: StoryDocumentRepository | None = None,
        get_theme_use_case=None,  # GetThemeUseCase — avoid circular import
    ) -> None:
        self._repository = repository
        self._generator = generator
        self._image_storage = image_storage
        self._video_generator = video_generator
        self._theme_repository = theme_repository
        self._scene_repository = scene_repository
        self._user_story_repository = user_story_repository
        self._media_tracker = media_tracker
        self._story_doc_repository = story_doc_repository
        self._get_theme_use_case = get_theme_use_case

    async def generate_questions(self, command: GenerateQuestionsCommand) -> QuestionsResult:
        """Generate questions then generate all option images inline (awaited)."""
        questions = await self._generator.generate_initial_questions(command.theme.strip())

        # Generate all option images in parallel and attach URIs directly.
        if self._image_storage is not None:
            await self._generate_question_images(questions)

        return QuestionsResult(theme=command.theme.strip(), questions=questions)

    async def _generate_question_images(self, questions: list) -> None:  # noqa: ANN001
        """Generate a 2x2 grid image per question, crop quadrants, upload each to GCS.

        This reduces Imagen calls from 16 (one per option) to 4 (one per question).
        """
        from io import BytesIO

        from PIL import Image

        async def _process_question(question) -> None:  # noqa: ANN001
            options = question.options
            prompts = [opt.image_prompt or "" for opt in options]

            # Pad to exactly 4 prompts (should already be 4)
            while len(prompts) < 4:
                prompts.append(prompts[-1] if prompts else "blank")

            try:
                grid_bytes = await self._generator.generate_option_image_grid(prompts[:4])
            except Exception:
                logger.exception("Failed to generate grid for question: %s", question.text)
                return

            # Crop the grid into 4 quadrants
            try:
                grid_img = Image.open(BytesIO(grid_bytes))
                w, h = grid_img.size
                mid_x, mid_y = w // 2, h // 2
                quadrants = [
                    grid_img.crop((0, 0, mid_x, mid_y)),          # top-left
                    grid_img.crop((mid_x, 0, w, mid_y)),          # top-right
                    grid_img.crop((0, mid_y, mid_x, h)),          # bottom-left
                    grid_img.crop((mid_x, mid_y, w, h)),          # bottom-right
                ]
            except Exception:
                logger.exception("Failed to crop grid image")
                return

            # Upload each quadrant and assign URI to matching option
            for idx, opt in enumerate(options[:4]):
                try:
                    buf = BytesIO()
                    quadrants[idx].save(buf, format="PNG")
                    img_bytes = buf.getvalue()
                    path = f"question-options/{uuid4()}.png"
                    uri = await self._image_storage.upload_image(img_bytes, path)  # type: ignore[union-attr]
                    opt.image_uri = uri
                except Exception:
                    logger.exception("Failed to upload cropped quadrant %d", idx)

        await asyncio.gather(*[_process_question(q) for q in questions])

    async def generate_opening_scene(
        self,
        command: GenerateOpeningSceneCommand,
        user_id: str = "",
    ) -> OpeningSceneResult:
        """Full orchestration: save answers → generate scene → persist to Firestore."""

        # 1. Mark story as generating
        if self._story_doc_repository is not None and user_id:
            self._story_doc_repository.update_status(
                user_id, command.story_id,
                "generating_opening_scene",
                {"questionnaireCompleted": True},
            )

        # 2. Fetch full theme detail for a richer LLM prompt
        from app.domain.models.theme_detail import PromptHints, ThemeDetail

        theme_detail: ThemeDetail = ThemeDetail(
            theme_id=command.theme_id,
            title=command.theme_id,  # bare fallback; overwritten below if lookup succeeds
            category="",
            description="",
        )
        if self._get_theme_use_case is not None:
            try:
                fetched = self._get_theme_use_case.execute(command.theme_id)
                theme_detail = fetched
            except Exception:
                logger.warning("Could not fetch theme %s; using minimal ThemeDetail", command.theme_id)

        # 3. Generate scene via LLM — pass the full ThemeDetail for richer context
        answers_tuples = [(a.question, a.selected_option) for a in command.answers]
        scene = await self._generator.generate_opening_scene_from_answers(
            theme=theme_detail,
            character_name=command.character_name.strip(),
            answers=answers_tuples,
        )

        # 4. Persist answers subcollection + custom input
        if self._story_doc_repository is not None and user_id:
            try:
                self._story_doc_repository.save_answers(
                    user_id,
                    command.story_id,
                    [
                        {
                            "questionId": a.question_id,
                            "question": a.question,
                            "selectedOption": a.selected_option,
                            "imageUrl": a.image_url,
                        }
                        for a in command.answers
                    ],
                    command.custom_input,
                )
            except Exception:
                logger.exception("Failed to save answers for story %s", command.story_id)

            # 5. Store scene_001 as the root scene of the branching tree
            try:
                self._story_doc_repository.store_scene(
                    user_id,
                    command.story_id,
                    "scene_001",
                    {
                        "sceneId": "scene_001",
                        "title": scene.scene_title,
                        "description": scene.scene_description,
                        "isRoot": True,
                        "depth": 0,
                        "parentSceneId": None,   # ← backwards link (null = root)
                        "nextSceneIds": [],       # ← forward links; populated as children are created
                        "choices": [
                            {
                                "choiceId": c.choice_id,
                                "choiceText": c.choice_text,
                                "directionHint": c.direction_hint,
                                "imagePrompt": c.image_prompt,
                                "videoPrompt": c.video_prompt,
                                "nextSceneId": None,
                                "imageUrl": None,
                                "videoUrl": None,
                            }
                            for c in scene.choices
                        ],
                    },
                )
            except Exception:
                logger.exception("Failed to store scene_001 for story %s", command.story_id)

            # 6. Anchor the story doc to the root scene — no linear counters, tree only
            try:
                self._story_doc_repository.update_status(
                    user_id, command.story_id,
                    "opening_scene_ready",
                    {
                        "rootSceneId": "scene_001",           # entry point of the tree
                        "branchDepth": 0,                      # deepest explored depth so far
                        "characterName": command.character_name.strip(),
                    },
                )
            except Exception:
                logger.exception("Failed to update story graph for story %s", command.story_id)

        return OpeningSceneResult(
            story_id=command.story_id,
            theme=theme_detail.title,
            character_name=command.character_name.strip(),
            scene=scene,
        )

    def fire_opening_scene_media(  # noqa: ANN001
        self,
        scene,
        story_id: str = "",
        user_id: str = "",
        scene_id: str = "scene_001",
    ) -> str | None:
        """Register opening-scene media as a request and kick off background generation.

        GCS paths: {user_id}/story/{story_id}/scene/{scene_id}/choice/{choice_id}/image.png|video.mp4
        After each asset upload completes, the matching Firestore choice is updated with its URL.
        Returns ``media_request_id`` (or ``None`` if storage is unavailable).
        """
        if self._image_storage is None or self._media_tracker is None:
            return None

        assets: list[AssetState] = []

        # Scene-level video — disabled
        # scene_video_prompt = scene.video_prompt or getattr(scene, "scene_description", "")
        # if scene_video_prompt and self._video_generator is not None:
        #     assets.append(AssetState(
        #         asset_key="scene_video",
        #         asset_type="video",
        #         prompt=scene_video_prompt,
        #     ))

        # Per-choice assets — fall back to image_prompt for video if video_prompt is empty
        for choice in scene.choices:
            if choice.image_prompt:
                assets.append(AssetState(
                    asset_key=f"choice_{choice.choice_id}_image",
                    asset_type="image",
                    prompt=choice.image_prompt,
                ))
            choice_video_prompt = choice.video_prompt or choice.image_prompt
            if choice_video_prompt and self._video_generator is not None:
                assets.append(AssetState(
                    asset_key=f"choice_{choice.choice_id}_video",
                    asset_type="video",
                    prompt=choice_video_prompt,
                ))

        if not assets:
            return None

        request_id = self._media_tracker.create_request(assets)
        asyncio.create_task(
            self._run_opening_scene_media(request_id, scene, story_id, user_id, scene_id)
        )
        return request_id

    async def _run_opening_scene_media(  # noqa: ANN001
        self,
        request_id: str,
        scene,
        story_id: str = "",
        user_id: str = "",
        scene_id: str = "scene_001",
    ) -> None:
        """Background coroutine: generate all opening-scene media in parallel.

        GCS path convention:
          {user_id}/story/{story_id}/scene/{scene_id}/choice/{choice_id}/image.png
          {user_id}/story/{story_id}/scene/{scene_id}/choice/{choice_id}/video.mp4
          {user_id}/story/{story_id}/scene/{scene_id}/scene_video.mp4
        After each upload, the Firestore scene document's matching choice is updated.
        """

        def _choice_path(choice_id: str, filename: str) -> str:
            if user_id and story_id:
                return f"{user_id}/story/{story_id}/scene/{scene_id}/choice/{choice_id}/{filename}"
            if story_id:
                return f"story/{story_id}/scene/{scene_id}/choice/{choice_id}/{filename}"
            return f"choice-{choice_id}/{uuid4()!s}-{filename}"

        def _scene_path(filename: str) -> str:
            if user_id and story_id:
                return f"{user_id}/story/{story_id}/scene/{scene_id}/{filename}"
            if story_id:
                return f"story/{story_id}/scene/{scene_id}/{filename}"
            return f"opening-scene/{uuid4()!s}-{filename}"

        def _write_choice_media(
            choice_id: str, *, image_url: str | None = None, video_url: str | None = None
        ) -> None:
            """Read-modify-write the choice array on the Firestore scene document."""
            if self._story_doc_repository is None or not (user_id and story_id):
                return
            try:
                self._story_doc_repository.update_scene_choice_media(
                    user_id, story_id, scene_id, choice_id,
                    image_url=image_url,
                    video_url=video_url,
                )
            except Exception:
                logger.exception("Failed to write choice %s media URL to Firestore", choice_id)

        async def _gen_image(asset_key: str, prompt: str, path: str, choice_id: str = "") -> None:
            try:
                image_bytes = await self._generator.generate_option_image(prompt)
                await self._image_storage.upload_image(image_bytes, path)  # type: ignore[union-attr]
                self._media_tracker.mark_completed(request_id, asset_key, path)  # store GCS path
                if choice_id:
                    _write_choice_media(choice_id, image_url=path)  # persist GCS path to Firestore
            except Exception as exc:
                self._media_tracker.mark_failed(request_id, asset_key, str(exc))  # type: ignore[union-attr]

        async def _gen_video(asset_key: str, prompt: str, path: str, choice_id: str = "") -> None:
            try:
                req = VideoGenerationRequest(
                    prompt=prompt,
                    model="veo-2.0-generate-001",
                    duration_seconds=5,
                    aspect_ratio="16:9",
                )
                result = await self._video_generator.generate(req)  # type: ignore[union-attr]
                await self._image_storage.upload_video(result.video_bytes, path)  # type: ignore[union-attr]
                self._media_tracker.mark_completed(request_id, asset_key, path)  # store GCS path
                if choice_id:
                    _write_choice_media(choice_id, video_url=path)  # persist GCS path to Firestore
            except Exception as exc:
                self._media_tracker.mark_failed(request_id, asset_key, str(exc))  # type: ignore[union-attr]

        tasks: list = []

        # Scene-level video — disabled
        # scene_video_prompt = scene.video_prompt or getattr(scene, "scene_description", "")
        # if scene_video_prompt and self._video_generator is not None:
        #     tasks.append(_gen_video(
        #         "scene_video", scene_video_prompt, _scene_path("scene_video.mp4"),
        #     ))

        for choice in scene.choices:
            if choice.image_prompt:
                tasks.append(_gen_image(
                    f"choice_{choice.choice_id}_image",
                    choice.image_prompt,
                    _choice_path(choice.choice_id, "image.png"),
                    choice.choice_id,
                ))
            # Fall back to image_prompt as video prompt if LLM omitted video_prompt
            choice_video_prompt = choice.video_prompt or choice.image_prompt
            if choice_video_prompt and self._video_generator is not None:
                tasks.append(_gen_video(
                    f"choice_{choice.choice_id}_video",
                    choice_video_prompt,
                    _choice_path(choice.choice_id, "video.mp4"),
                    choice.choice_id,
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

    def list_active_stories(self, user_id: str) -> list[StoryCardView]:
        resolved_user_id = user_id.strip()
        if self._user_story_repository is not None and resolved_user_id:
            records = self._user_story_repository.list_by_user_id(resolved_user_id)
            return [self._to_story_card_view_from_record(record) for record in records]

        sessions = sorted(
            self._repository.list_all(),
            key=lambda item: item.updated_at,
            reverse=True,
        )
        return [self._to_story_card_view(state=story) for story in sessions]

    def get_scene_choice_media(
        self, user_id: str, story_id: str, scene_id: str
    ) -> list[dict] | None:
        """Return current imageUrl / videoUrl for every choice in a scene.

        Reads live from Firestore so values reflect generation progress.
        Returns None if the scene document does not exist.
        Each item: {"choice_id": str, "image_url": str|None, "video_url": str|None}
        """
        if self._story_doc_repository is None:
            return None
        scene_data = self._story_doc_repository.get_scene(
            user_id.strip(), story_id.strip(), scene_id.strip()
        )
        if scene_data is None:
            return None
        result = []
        for c in scene_data.get("choices", []):
            result.append({
                "choice_id": c.get("choiceId", ""),
                "image_url": c.get("imageUrl"),
                "video_url": c.get("videoUrl"),
            })
        return result

    def get_story_detail(self, user_id: str, story_id: str) -> StoryDetailView | None:
        """Return full story detail view for a given user and story."""
        resolved_user_id = user_id.strip()
        resolved_story_id = story_id.strip()

        if self._user_story_repository is not None and resolved_user_id and resolved_story_id:
            record = self._user_story_repository.get_by_user_id_and_story_id(
                user_id=resolved_user_id,
                story_id=resolved_story_id,
            )
            if record is not None:
                return self._to_story_detail_view_from_record(record)

        # Fallback for local/dev runs that only have in-memory sessions.
        fallback_state = self._repository.get(resolved_story_id)
        if fallback_state is None:
            return None
        card = self._to_story_card_view(fallback_state)
        return StoryDetailView(
            story_id=card.story_id,
            user_id=resolved_user_id or "dev-user",
            session_id=card.session_id,
            title=card.title,
            genre=card.genre,
            character_name=card.character_name,
            archetype=card.archetype,
            last_scene_id=card.last_scene_id,
            updated_at=card.updated_at,
            choices_available=card.choices_available,
            progress=card.progress,
            cover_image=card.cover_image,
            last_played_at=card.last_played_at,
            status=card.status,
            created_at=fallback_state.created_at,
            theme_category=card.genre,
        )

    def list_story_themes(self) -> list[StoryThemeView]:
        if self._theme_repository is None:
            return []

        return [
            StoryThemeView(
                id=theme.theme_id,
                title=theme.title,
                tagline=theme.tagline,
                description=theme.description,
                image=theme.image,
                accent_color=theme.accent_color,
            )
            for theme in self._theme_repository.list_active()
        ]

    def list_story_scenes(self, story_id: str) -> list[StorySceneView]:
        if self._scene_repository is None:
            return []

        records = self._scene_repository.list_by_story_id(story_id.strip())
        return [
            StorySceneView(
                scene_id=item.scene_id,
                story_id=item.story_id,
                chapter_number=item.chapter_number,
                scene_number=item.scene_number,
                title=item.title,
                description=item.description,
                short_summary=item.short_summary,
                full_narrative=item.full_narrative,
                parent_scene_id=item.parent_scene_id,
                selected_choice_id_from_parent=item.selected_choice_id_from_parent,
                path_depth=item.path_depth,
                is_root=item.is_root,
                is_current_checkpoint=item.is_current_checkpoint,
                is_ending=item.is_ending,
                ending_type=item.ending_type,
                scene_type=item.scene_type,
                mood=item.mood,
                location=(
                    StorySceneLocationView(
                        name=item.location.name,
                        location_type=item.location.location_type,
                    )
                    if item.location is not None
                    else None
                ),
                characters_present=item.characters_present,
                asset_refs=StorySceneAssetRefsView(
                    hero_image_id=item.asset_refs.hero_image_id,
                    scene_image_id=item.asset_refs.scene_image_id,
                    scene_video_id=item.asset_refs.scene_video_id,
                    scene_audio_id=item.asset_refs.scene_audio_id,
                ),
                generation_status=StorySceneGenerationStatusView(
                    text=item.generation_status.text,
                    image=item.generation_status.image,
                    video=item.generation_status.video,
                ),
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in records
        ]

    @staticmethod
    def _to_story_card_view(state: StoryState) -> StoryCardView:
        return StoryCardView(
            story_id=state.session_id,
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
    def _to_story_card_view_from_record(record: UserStoryRecord) -> StoryCardView:
        session_id = (record.session_id or record.story_id).strip()
        return StoryCardView(
            story_id=record.story_id,
            session_id=session_id,
            title=record.title,
            genre=record.genre,
            character_name=record.character_name,
            archetype=record.archetype,
            last_scene_id=record.last_scene_id,
            updated_at=record.updated_at,
            choices_available=record.choices_available,
            progress=record.progress,
            cover_image=record.cover_image,
            last_played_at=record.last_played_at,
            status=record.status,
            theme_id=record.theme_id,
            theme_title=record.theme_title,
            theme_description=record.theme_description,
        )

    @staticmethod
    def _to_story_detail_view_from_record(record: UserStoryRecord) -> StoryDetailView:
        session_id = (record.session_id or record.story_id).strip()
        return StoryDetailView(
            story_id=record.story_id,
            user_id=record.user_id,
            session_id=session_id,
            title=record.title,
            genre=record.genre,
            character_name=record.character_name,
            archetype=record.archetype,
            last_scene_id=record.last_scene_id,
            updated_at=record.updated_at,
            choices_available=record.choices_available,
            progress=record.progress,
            cover_image=record.cover_image,
            last_played_at=record.last_played_at,
            status=record.status,
            theme_id=record.theme_id,
            theme_title=record.theme_title,
            theme_category=record.theme_category,
            theme_description=record.theme_description,
            question_count=record.question_count,
            questions_generated=record.questions_generated,
            created_at=record.created_at,
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
