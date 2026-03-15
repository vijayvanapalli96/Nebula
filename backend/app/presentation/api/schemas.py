from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.application.dto.story_commands import ApplyActionCommand, GenerateOpeningSceneCommand, GenerateQuestionsCommand, QuestionAnswer, StartStoryCommand
from app.application.dto.story_results import OpeningSceneResult, QuestionsResult, StoryActionResult, StoryCardView, StoryStartResult
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
    session_id: str
    title: str
    genre: str
    character_name: str
    archetype: str
    last_scene_id: str | None = None
    updated_at: datetime
    choices_available: int = 0


class GenerateQuestionsRequest(BaseModel):
    theme: str = Field(..., min_length=1, description="Story theme to generate questions for.")


class QuestionOptionResponse(BaseModel):
    text: str = Field(..., min_length=1, description="Option text.")
    image_prompt: str = Field(..., description="Prompt used to generate the option image.")


class QuestionResponse(BaseModel):
    question: str = Field(..., min_length=1, description="The question text.")
    options: list[QuestionOptionResponse] = Field(..., min_length=4, max_length=4, description="Answer options.")


class GenerateQuestionsResponse(BaseModel):
    theme: str
    questions: list[QuestionResponse] = Field(..., min_length=1)
    media_request_id: str | None = Field(default=None, description="Poll /story/media/{id} for image URIs.")


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
        session_id=view.session_id,
        title=view.title,
        genre=view.genre,
        character_name=view.character_name,
        archetype=view.archetype,
        last_scene_id=view.last_scene_id,
        updated_at=view.updated_at,
        choices_available=view.choices_available,
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


def to_questions_response(
    result: QuestionsResult,
    media_request_id: str | None = None,
) -> GenerateQuestionsResponse:
    return GenerateQuestionsResponse(
        theme=result.theme,
        questions=[
            QuestionResponse(
                question=q.question,
                options=[
                    QuestionOptionResponse(text=opt.text, image_prompt=opt.image_prompt)
                    for opt in q.options
                ],
            )
            for q in result.questions
        ],
        media_request_id=media_request_id,
    )

