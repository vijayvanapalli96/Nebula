from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.application.dto.story_commands import ApplyActionCommand, GenerateOpeningSceneCommand, GenerateQuestionsCommand, QuestionAnswer, StartStoryCommand
from app.application.dto.story_results import (
    OpeningSceneResult,
    QuestionsResult,
    StoryActionResult,
    StoryCardView,
    StoryDetailView,
    StorySceneView,
    StoryStartResult,
    StoryThemeView,
)
from app.domain.models.story import HistoryEntry, Scene, StoryState


class SceneMetadataResponse(BaseModel):
    scene_id: str = Field(..., description="Unique scene identifier.")
    chapter: int = Field(..., ge=1, description="Story chapter/turn index.")
    mood: str = Field(..., min_length=1, description="Current tone of the scene.")
    tension: int = Field(..., ge=0, le=100, description="Tension score from 0 to 100.")


class SceneChoiceResponse(BaseModel):
    choice_id: str = Field(..., description="Frontend-visible choice identifier.")
    label: str = Field(..., min_length=1, description="Choice label shown to the player.")
    consequence_hint: str | None = Field(
        default=None,
        description="Optional short hint about likely consequence.",
    )


class SceneResponse(BaseModel):
    metadata: SceneMetadataResponse
    visual_prompt: str = Field(..., min_length=1, description="Image generation prompt.")
    narrative_text: str = Field(..., min_length=1, description="Cinematic scene prose.")
    choices: list[SceneChoiceResponse] = Field(..., min_length=2, max_length=4)


class HistoryEntryResponse(BaseModel):
    turn: int = Field(..., ge=1)
    entry_type: Literal["scene", "choice"]
    content: str = Field(..., min_length=1)
    choice_id: str | None = None
    scene_id: str | None = None
    created_at: datetime


class StoryStateResponse(BaseModel):
    session_id: str
    genre: str
    character_name: str
    archetype: str
    motivation: str
    history_log: list[HistoryEntryResponse] = Field(default_factory=list)
    current_scene: SceneResponse | None = None
    created_at: datetime
    updated_at: datetime


class StoryStartRequest(BaseModel):
    genre: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    archetype: str = Field(..., min_length=1)
    motivation: str = Field(..., min_length=1)


class StoryStartResponse(BaseModel):
    session_id: str
    scene: SceneResponse


class StoryActionRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    choice_id: str = Field(..., min_length=1)


class StoryActionResponse(BaseModel):
    session_id: str
    scene: SceneResponse


class StoryCardResponse(BaseModel):
    story_id: str
    session_id: str
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None = None
    updated_at: datetime
    choices_available: int = 0
    progress: int | None = None
    cover_image: str | None = None
    last_played_at: datetime | None = None
    status: str | None = None


class StoryDetailResponse(BaseModel):
    story_id: str
    user_id: str
    session_id: str
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None = None
    updated_at: datetime
    choices_available: int = 0
    progress: int | None = None
    cover_image: str | None = None
    last_played_at: datetime | None = None
    status: str | None = None
    theme_id: str | None = None
    theme_title: str | None = None
    theme_category: str | None = None
    theme_description: str | None = None
    question_count: int | None = None
    questions_generated: list[str] = Field(default_factory=list)
    created_at: datetime | None = None


class StoryThemeResponse(BaseModel):
    id: str
    title: str
    tagline: str
    description: str
    image: str
    accent_color: str


class StorySceneLocationResponse(BaseModel):
    name: str
    type: str


class StorySceneAssetRefsResponse(BaseModel):
    hero_image_id: str | None = None
    scene_image_id: str | None = None
    scene_video_id: str | None = None
    scene_audio_id: str | None = None


class StorySceneGenerationStatusResponse(BaseModel):
    text: str
    image: str
    video: str


class StorySceneResponse(BaseModel):
    scene_id: str
    story_id: str
    chapter_number: int = Field(..., ge=1)
    scene_number: int = Field(..., ge=1)
    title: str
    description: str
    short_summary: str
    full_narrative: str
    parent_scene_id: str | None = None
    selected_choice_id_from_parent: str | None = None
    path_depth: int = Field(default=0, ge=0)
    is_root: bool
    is_current_checkpoint: bool
    is_ending: bool
    ending_type: str | None = None
    scene_type: str
    mood: str
    location: StorySceneLocationResponse | None = None
    characters_present: list[str] = Field(default_factory=list)
    asset_refs: StorySceneAssetRefsResponse
    generation_status: StorySceneGenerationStatusResponse
    created_at: datetime
    updated_at: datetime


class GenerateQuestionsRequest(BaseModel):
    theme: str = Field(..., min_length=1, description="Story theme to generate questions for.")


class QuestionOptionResponse(BaseModel):
    text: str = Field(..., min_length=1, description="Option text.")
    image_prompt: str = Field(..., description="Prompt used to generate the option image.")
    image_uri: str | None = Field(default=None, description="GCS signed URL for the generated image.")


class QuestionResponse(BaseModel):
    question: str = Field(..., min_length=1, description="The question text.")
    options: list[QuestionOptionResponse] = Field(..., min_length=4, max_length=4, description="Answer options.")


class GenerateQuestionsResponse(BaseModel):
    theme: str
    questions: list[QuestionResponse] = Field(..., min_length=1)


class AnswerInput(BaseModel):
    question: str = Field(..., min_length=1, description="The question text.")
    answer: str = Field(..., min_length=1, description="The selected answer.")


class OpeningSceneRequest(BaseModel):
    theme: str = Field(..., min_length=1, description="Story theme.")
    character_name: str = Field(..., min_length=1, description="Player character name.")
    answers: list[AnswerInput] = Field(..., min_length=1, description="Answered questions.")


class OpeningChoiceResponse(BaseModel):
    choice_id: str = Field(..., description="Choice identifier.")
    choice_text: str = Field(..., min_length=1, description="Choice text shown to the player.")
    direction_hint: str = Field(..., min_length=1, description="Hint about narrative direction.")
    image_prompt: str = Field(default="", description="Prompt for choice preview image.")
    video_prompt: str = Field(default="", description="Prompt for choice action video.")


class OpeningSceneResponse(BaseModel):
    theme: str
    character_name: str
    scene_title: str
    scene_description: str
    video_prompt: str = Field(default="", description="Prompt for the opening scene video.")
    choices: list[OpeningChoiceResponse] = Field(..., min_length=2)
    media_request_id: str | None = Field(default=None, description="Poll /story/media/{id} for media URIs.")


class MediaResponse(BaseModel):
    """Simple map of asset_key → GCS URI (null if not ready yet)."""
    request_id: str
    assets: dict[str, str | None] = Field(
        ..., description="Map of asset key to GCS signed URL. null if still generating.",
    )


def to_start_command(request: StoryStartRequest) -> StartStoryCommand:
    return StartStoryCommand(
        genre=request.genre,
        name=request.name,
        archetype=request.archetype,
        motivation=request.motivation,
    )


def to_action_command(request: StoryActionRequest) -> ApplyActionCommand:
    return ApplyActionCommand(session_id=request.session_id, choice_id=request.choice_id)


def to_start_response(result: StoryStartResult) -> StoryStartResponse:
    return StoryStartResponse(session_id=result.session_id, scene=to_scene_response(result.scene))


def to_action_response(result: StoryActionResult) -> StoryActionResponse:
    return StoryActionResponse(session_id=result.session_id, scene=to_scene_response(result.scene))


def to_story_card_response(view: StoryCardView) -> StoryCardResponse:
    return StoryCardResponse(
        story_id=view.story_id,
        session_id=view.session_id,
        title=view.title,
        genre=view.genre,
        character_name=view.character_name,
        archetype=view.archetype,
        last_scene_id=view.last_scene_id,
        updated_at=view.updated_at,
        choices_available=view.choices_available,
        progress=view.progress,
        cover_image=view.cover_image,
        last_played_at=view.last_played_at,
        status=view.status,
    )


def to_story_detail_response(view: StoryDetailView) -> StoryDetailResponse:
    return StoryDetailResponse(
        story_id=view.story_id,
        user_id=view.user_id,
        session_id=view.session_id,
        title=view.title,
        genre=view.genre,
        character_name=view.character_name,
        archetype=view.archetype,
        last_scene_id=view.last_scene_id,
        updated_at=view.updated_at,
        choices_available=view.choices_available,
        progress=view.progress,
        cover_image=view.cover_image,
        last_played_at=view.last_played_at,
        status=view.status,
        theme_id=view.theme_id,
        theme_title=view.theme_title,
        theme_category=view.theme_category,
        theme_description=view.theme_description,
        question_count=view.question_count,
        questions_generated=view.questions_generated or [],
        created_at=view.created_at,
    )


def to_story_theme_response(view: StoryThemeView) -> StoryThemeResponse:
    return StoryThemeResponse(
        id=view.id,
        title=view.title,
        tagline=view.tagline,
        description=view.description,
        image=view.image,
        accent_color=view.accent_color,
    )


def to_story_scene_response(view: StorySceneView) -> StorySceneResponse:
    return StorySceneResponse(
        scene_id=view.scene_id,
        story_id=view.story_id,
        chapter_number=view.chapter_number,
        scene_number=view.scene_number,
        title=view.title,
        description=view.description,
        short_summary=view.short_summary,
        full_narrative=view.full_narrative,
        parent_scene_id=view.parent_scene_id,
        selected_choice_id_from_parent=view.selected_choice_id_from_parent,
        path_depth=view.path_depth,
        is_root=view.is_root,
        is_current_checkpoint=view.is_current_checkpoint,
        is_ending=view.is_ending,
        ending_type=view.ending_type,
        scene_type=view.scene_type,
        mood=view.mood,
        location=(
            StorySceneLocationResponse(
                name=view.location.name,
                type=view.location.location_type,
            )
            if view.location is not None
            else None
        ),
        characters_present=view.characters_present,
        asset_refs=StorySceneAssetRefsResponse(
            hero_image_id=view.asset_refs.hero_image_id,
            scene_image_id=view.asset_refs.scene_image_id,
            scene_video_id=view.asset_refs.scene_video_id,
            scene_audio_id=view.asset_refs.scene_audio_id,
        ),
        generation_status=StorySceneGenerationStatusResponse(
            text=view.generation_status.text,
            image=view.generation_status.image,
            video=view.generation_status.video,
        ),
        created_at=view.created_at,
        updated_at=view.updated_at,
    )


def to_scene_response(scene: Scene) -> SceneResponse:
    return SceneResponse(
        metadata=SceneMetadataResponse(
            scene_id=scene.metadata.scene_id,
            chapter=scene.metadata.chapter,
            mood=scene.metadata.mood,
            tension=scene.metadata.tension,
        ),
        visual_prompt=scene.visual_prompt,
        narrative_text=scene.narrative_text,
        choices=[
            SceneChoiceResponse(
                choice_id=choice.choice_id,
                label=choice.label,
                consequence_hint=choice.consequence_hint,
            )
            for choice in scene.choices
        ],
    )


def to_story_state_response(state: StoryState) -> StoryStateResponse:
    return StoryStateResponse(
        session_id=state.session_id,
        genre=state.genre,
        character_name=state.character_name,
        archetype=state.archetype,
        motivation=state.motivation,
        history_log=[to_history_entry_response(item) for item in state.history_log],
        current_scene=to_scene_response(state.current_scene) if state.current_scene else None,
        created_at=state.created_at,
        updated_at=state.updated_at,
    )


def to_history_entry_response(entry: HistoryEntry) -> HistoryEntryResponse:
    return HistoryEntryResponse(
        turn=entry.turn,
        entry_type=entry.entry_type,
        content=entry.content,
        choice_id=entry.choice_id,
        scene_id=entry.scene_id,
        created_at=entry.created_at,
    )


def to_questions_command(request: GenerateQuestionsRequest) -> GenerateQuestionsCommand:
    return GenerateQuestionsCommand(theme=request.theme)


def to_opening_scene_command(request: OpeningSceneRequest) -> GenerateOpeningSceneCommand:
    return GenerateOpeningSceneCommand(
        theme=request.theme,
        character_name=request.character_name,
        answers=[QuestionAnswer(question=a.question, answer=a.answer) for a in request.answers],
    )


def to_opening_scene_response(
    result: OpeningSceneResult,
    media_request_id: str | None = None,
) -> OpeningSceneResponse:
    return OpeningSceneResponse(
        theme=result.theme,
        character_name=result.character_name,
        scene_title=result.scene.scene_title,
        scene_description=result.scene.scene_description,
        video_prompt=result.scene.video_prompt,
        choices=[
            OpeningChoiceResponse(
                choice_id=c.choice_id,
                choice_text=c.choice_text,
                direction_hint=c.direction_hint,
                image_prompt=c.image_prompt,
                video_prompt=c.video_prompt,
            )
            for c in result.scene.choices
        ],
        media_request_id=media_request_id,
    )


def to_questions_response(result: QuestionsResult) -> GenerateQuestionsResponse:
    return GenerateQuestionsResponse(
        theme=result.theme,
        questions=[
            QuestionResponse(
                question=q.question,
                options=[
                    QuestionOptionResponse(
                        text=opt.text,
                        image_prompt=opt.image_prompt,
                        image_uri=opt.image_uri,
                    )
                    for opt in q.options
                ],
            )
            for q in result.questions
        ],
    )
