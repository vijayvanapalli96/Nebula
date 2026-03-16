"""Use case: orchestrate the full story-questions generation pipeline.

Steps:
  1. Fetch theme from Firestore (GetThemeUseCase)
  2. Create story document in Firestore (CreateStoryUseCase)
  3. Generate 4 questions via LLM (ThemedQuestionGeneratorPort)
  4. Generate & upload per-option images to GCS
  5. Persist each question document in Firestore
  6. Update story status → "questions_generated"
  7. Return result to the caller
"""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from app.application.ports.image_storage import ImageStoragePort
from app.application.ports.story_generator import StoryGeneratorPort
from app.application.ports.themed_question_generator import ThemedQuestionGeneratorPort
from app.application.use_cases.create_story import CreateStoryUseCase
from app.application.use_cases.get_theme import GetThemeUseCase
from app.domain.models.story import InitialQuestion
from app.domain.models.story_document import StoredQuestion, StoredQuestionOption
from app.domain.repositories.story_document_repository import StoryDocumentRepository

logger = logging.getLogger(__name__)


class GenerateStoryQuestionsUseCase:
    def __init__(
        self,
        get_theme_use_case: GetThemeUseCase,
        create_story_use_case: CreateStoryUseCase,
        question_generator: ThemedQuestionGeneratorPort,
        story_generator: StoryGeneratorPort,
        image_storage: ImageStoragePort | None,
        story_doc_repository: StoryDocumentRepository,
    ) -> None:
        self._get_theme = get_theme_use_case
        self._create_story = create_story_use_case
        self._question_generator = question_generator
        self._story_generator = story_generator
        self._image_storage = image_storage
        self._story_doc_repository = story_doc_repository

    async def execute(self, user_id: str, theme_id: str):  # noqa: ANN201
        """Run the full pipeline and return a GenerateStoryQuestionsResult."""
        from app.application.dto.story_results import GenerateStoryQuestionsResult

        # ── 1. Fetch theme ────────────────────────────────────────────────────
        theme = self._get_theme.execute(theme_id)

        # ── 2. Create story document (status = "initializing") ────────────────
        story_id = self._create_story.execute(user_id, theme)

        # ── 3. LLM question generation ────────────────────────────────────────
        questions = await self._question_generator.generate_themed_questions(theme)

        # ── 4. Image generation & GCS upload ─────────────────────────────────
        if self._image_storage is not None:
            await self._generate_and_upload_images(
                user_id=user_id,
                story_id=story_id,
                questions=questions,
            )

        # ── 5. Persist questions ──────────────────────────────────────────────
        now = datetime.now(UTC)
        for idx, question in enumerate(questions):
            q_id = question.question_id or f"q{idx}"
            stored_options = [
                StoredQuestionOption(
                    text=opt.text,
                    image_prompt=opt.image_prompt,
                    image_url=opt.image_uri or "",
                    gcs_path=opt.gcs_path or "",
                )
                for opt in question.options
            ]
            self._story_doc_repository.store_question(
                user_id=user_id,
                story_id=story_id,
                question=StoredQuestion(
                    question_id=q_id,
                    question=question.question,
                    options=stored_options,
                    created_at=now,
                ),
            )

        # ── 6. Update story status ────────────────────────────────────────────
        self._story_doc_repository.update_status(
            user_id=user_id,
            story_id=story_id,
            status="questions_generated",
            summary={
                "questionsGenerated": True,
                "questionCount": len(questions),
            },
        )

        return GenerateStoryQuestionsResult(
            story_id=story_id,
            theme=theme.title,
            questions=questions,
        )

    # ── Image helpers ─────────────────────────────────────────────────────────

    async def _generate_and_upload_images(
        self,
        user_id: str,
        story_id: str,
        questions: list[InitialQuestion],
    ) -> None:
        """Generate a 2×2 grid image per question, crop quadrants, upload each.

        GCS destination path:
            {user_id}/stories/{story_id}/generated_questions/{question_id}/{option_index}.png
        """
        from io import BytesIO

        from PIL import Image

        async def _process_question(question: InitialQuestion, q_index: int) -> None:
            options = question.options
            prompts = [opt.image_prompt or "" for opt in options]
            # Ensure exactly 4 prompts
            while len(prompts) < 4:
                prompts.append(prompts[-1] if prompts else "abstract scene")

            try:
                grid_bytes = await self._story_generator.generate_option_image_grid(prompts[:4])
            except Exception:
                logger.exception(
                    "Grid image generation failed for question '%s'", question.question
                )
                return

            try:
                grid_img = Image.open(BytesIO(grid_bytes))
                w, h = grid_img.size
                mx, my = w // 2, h // 2
                quadrants = [
                    grid_img.crop((0, 0, mx, my)),       # top-left
                    grid_img.crop((mx, 0, w, my)),        # top-right
                    grid_img.crop((0, my, mx, h)),        # bottom-left
                    grid_img.crop((mx, my, w, h)),        # bottom-right
                ]
            except Exception:
                logger.exception("Grid crop failed for question '%s'", question.question)
                return

            q_id = question.question_id or f"q{q_index}"
            for opt_idx, opt in enumerate(options[:4]):
                try:
                    buf = BytesIO()
                    quadrants[opt_idx].save(buf, format="PNG")
                    img_bytes = buf.getvalue()
                    path = (
                        f"{user_id}/stories/{story_id}"
                        f"/generated_questions/{q_id}/{opt_idx}.png"
                    )
                    uri = await self._image_storage.upload_image(img_bytes, path)  # type: ignore[union-attr]
                    opt.image_uri = uri
                    opt.gcs_path = path
                except Exception:
                    logger.exception(
                        "Failed to upload image for question '%s' option %d",
                        q_id,
                        opt_idx,
                    )

        await asyncio.gather(
            *[_process_question(q, i) for i, q in enumerate(questions)]
        )
