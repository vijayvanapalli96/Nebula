from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.models.theme_detail import ThemeDetail

from app.domain.models.story import HistoryEntry, SceneChoice, StoryState
from app.domain.models.theme_detail import ThemeDetail

INITIAL_QUESTIONS_SYSTEM_PROMPT = """
You are an AI narrative designer creating the setup for an interactive story.

Your task is to generate 4 multiple-choice questions that will shape the core direction of the story.

The questions should help determine:
- the protagonist's role or background
- the central conflict or mystery
- the emotional tone or mood
- a key story element that can influence future plot events

Each question should meaningfully influence how the story unfolds in later scenes.

Rules:
- Questions must be clear and easy to answer
- Avoid vague or overly philosophical questions
- Each question must provide 4 distinct options
- Options should represent different narrative directions
- Questions should help shape the plot, character motivations, or story stakes
- Avoid repeating similar question types
- Each option must include an image_prompt: a vivid, single-sentence visual description
  suitable for an image generation model (no text, no UI elements, just a scene or object)

Return the result strictly in JSON format:

{
  "questions": [
    {
      "id": "",
      "question": "",
      "story_influence": "",
      "options": [
        {"text": "", "image_prompt": ""},
        {"text": "", "image_prompt": ""},
        {"text": "", "image_prompt": ""},
        {"text": "", "image_prompt": ""}
      ]
    }
  ]
}

Field explanations:
- id: a short identifier for the question
- question: the question shown to the user
- story_influence: explain how this question will affect the story generation
- options: four selectable choices, each with display text and a cinematic image_prompt
- image_prompt: a vivid visual description of the option for image generation (e.g. "A lone warrior standing on a cliff edge overlooking a stormy ocean at sunset")
"""

SYSTEM_PROMPT = """
You are a story engine for an interactive cinematic game.
Output must be valid JSON only, with no markdown fences and no extra text.
Rules:
- Keep narrative_text vivid, cinematic, and concise (80-130 words).
- Return exactly 3 choices, each meaningful and distinct.
- Keep stakes escalating and emotionally grounded.
- Make visual_prompt a single-line, image-model friendly description.
- metadata.tension must be an integer from 0 to 100.
Required JSON shape:
{
  "metadata": {"scene_id": "string", "chapter": 1, "mood": "string", "tension": 0},
  "visual_prompt": "string",
  "narrative_text": "string",
  "choices": [
    {"choice_id": "A", "label": "string", "consequence_hint": "string"},
    {"choice_id": "B", "label": "string", "consequence_hint": "string"},
    {"choice_id": "C", "label": "string", "consequence_hint": "string"}
  ]
}
"""

STYLE_SEEDS: dict[str, str] = {
    "noir": "Film noir, high contrast, rain-slick reflections, cigarette smoke haze",
    "fantasy": "Epic fantasy matte painting, volumetric light, ornate texture, cinematic scope",
    "sci-fi": "Futuristic production design, neon accents, holographic interfaces, atmospheric depth",
    "horror": "Low-key lighting, oppressive shadows, unsettling negative space, dread-filled composition",
    "romance": "Soft diffusion glow, intimate framing, warm palette, emotionally charged atmosphere",
    "thriller": "Tense cinematic framing, sharp contrasts, kinetic motion blur, urgent mood",
}

DEFAULT_STYLE_SEED = "Cinematic still frame, dramatic lighting, rich texture detail, 35mm film look"


def append_style_seed(genre: str, visual_prompt: str) -> str:
    seed = STYLE_SEEDS.get(genre.strip().lower(), DEFAULT_STYLE_SEED)
    clean_prompt = visual_prompt.strip()
    if seed.lower() in clean_prompt.lower():
        return clean_prompt
    return f"{clean_prompt}, {seed}"


def build_opening_prompt(state: StoryState) -> str:
    return (
        "Create the opening scene for this player character.\n"
        f"Genre: {state.genre}\n"
        f"Character Name: {state.character_name}\n"
        f"Archetype: {state.archetype}\n"
        f"Motivation: {state.motivation}\n"
        "The scene should establish immediate conflict and a clear next decision."
    )


def build_action_prompt(state: StoryState, chosen: SceneChoice) -> str:
    history = _history_to_text(state.history_log[-8:])
    current_scene_summary = state.current_scene.narrative_text if state.current_scene else ""
    return (
        "Continue the story based on the player's selected action.\n"
        f"Genre: {state.genre}\n"
        f"Character: {state.character_name} ({state.archetype})\n"
        f"Motivation: {state.motivation}\n"
        f"Previous scene narrative: {current_scene_summary}\n"
        f"Player selected choice_id={chosen.choice_id}, label='{chosen.label}'.\n"
        "Story log:\n"
        f"{history}\n"
        "Return the next scene with stronger stakes while preserving continuity."
    )


def _history_to_text(history: list[HistoryEntry]) -> str:
    if not history:
        return "No history yet."

    lines: list[str] = []
    for item in history:
        if item.entry_type == "choice":
            lines.append(f"Turn {item.turn}: PLAYER CHOICE {item.choice_id} - {item.content}")
        else:
            lines.append(f"Turn {item.turn}: SCENE {item.scene_id or ''} - {item.content}")
    return "\n".join(lines)


def build_questions_prompt(theme: str) -> str:
    return (
        f"The story theme is: {theme}\n"
        "Generate 4 simple multiple-choice questions that will shape the story world "
        "and the main character.\n"
        "Each question must have exactly 4 options."
    )


OPENING_SCENE_SYSTEM_PROMPT = """
You are a master storyteller creating the opening scene of an interactive cinematic story.
Output must be valid JSON only, with no markdown fences and no extra text.
Rules:
- scene_description must be immersive, vivid, and cinematic (120-150 words).
- Build immediate tension or mystery that hooks the reader.
- Use the character name and their answers to shape the world.
- Provide 3-4 branching choices, each leading in a meaningfully different direction.
- Each choice must have a short direction_hint describing the narrative consequence.
- video_prompt (scene level): a vivid 1-2 sentence cinematic motion description of the
  opening scene, suitable for a video generation model. Describe camera movement, action,
  atmosphere. No UI text, no titles.
- Each choice must include:
  - image_prompt: a vivid single-sentence visual still-frame description suitable for an
    image generation model (what the player would see if they pick this path).
  - video_prompt: a vivid 1-2 sentence cinematic motion description of what unfolds when
    the player picks this choice. Describe camera angle, action, atmosphere.
Required JSON shape:
{
  "scene_title": "string",
  "scene_description": "string",
  "video_prompt": "string",
  "choices": [
    {
      "choice_id": "A",
      "choice_text": "string",
      "direction_hint": "string",
      "image_prompt": "string",
      "video_prompt": "string"
    }
  ]
}
"""


def build_opening_scene_prompt(
    theme: "ThemeDetail", character_name: str, answers: list[tuple[str, str]]
) -> str:
    answers_block = "\n".join(
        f"  Q: {question}\n  A: {answer}" for question, answer in answers
    )
    tone_tags = ", ".join(theme.default_tone_tags) if theme.default_tone_tags else "none specified"
    return (
        f"Theme Title     : {theme.title}\n"
        f"Category        : {theme.category}\n"
        f"Description     : {theme.description}\n"
        f"Tone Tags       : {tone_tags}\n"
        f"Narrative Style : {theme.prompt_hints.narrative_style}\n"
        f"Visual Style    : {theme.prompt_hints.visual_style}\n"
        f"Character Name  : {character_name}\n"
        "The player answered these world-building questions:\n"
        f"{answers_block}\n\n"
        "Using the full theme context and the player's answers as creative seeds, "
        "write the opening scene that drops the character into the world with "
        "immediate tension and a clear hook. Match the theme's tone, narrative "
        "style, and visual style throughout."
    )


# ── Themed questions (richer theme context) ───────────────────────────────────

THEMED_QUESTIONS_SYSTEM_PROMPT = """
You are an expert narrative designer crafting personalised story-setup questions.

Task: generate EXACTLY 4 multiple-choice questions tailored to the provided theme.
These questions will shape the protagonist, central conflict, tone, and key story element.

Rules:
- Every question and option must feel native to the theme — title, category, tone, and style.
- Each question must have EXACTLY 4 options.
- Each option must include:
    text        : the choice shown to the player
    image_prompt: a vivid, single-sentence cinematic still-frame description for an
                  image generation model. Match the theme's visual style.
                  No text overlays, no UI elements, no titles.
- Question ids must be short snake_case strings (e.g. hero_role, central_conflict).
- story_influence: one sentence explaining how the answer shapes future scenes.
- Avoid vague philosophical questions; keep them concrete and narratively interesting.

Return ONLY valid JSON — no markdown fences, no extra text:

{
  "questions": [
    {
      "id": "snake_case_id",
      "question": "Question text shown to the player",
      "story_influence": "One-sentence note on narrative impact",
      "options": [
        {"text": "Option A text", "image_prompt": "Vivid cinematic description A"},
        {"text": "Option B text", "image_prompt": "Vivid cinematic description B"},
        {"text": "Option C text", "image_prompt": "Vivid cinematic description C"},
        {"text": "Option D text", "image_prompt": "Vivid cinematic description D"}
      ]
    }
  ]
}
"""


def build_themed_questions_prompt(theme: ThemeDetail) -> str:
    """Build the user-turn prompt that gives the LLM the full theme context."""
    tone_tags = ", ".join(theme.default_tone_tags) if theme.default_tone_tags else "none specified"
    return (
        f"Theme Title     : {theme.title}\n"
        f"Category        : {theme.category}\n"
        f"Description     : {theme.description}\n"
        f"Tone Tags       : {tone_tags}\n"
        f"Narrative Style : {theme.prompt_hints.narrative_style}\n"
        f"Visual Style    : {theme.prompt_hints.visual_style}\n\n"
        "Generate exactly 4 story-setup questions deeply rooted in this theme.\n"
        "Each question must have exactly 4 options with matching image_prompts.\n"
        "Return strictly valid JSON as specified."
    )


# ── Continuation scene (scene → choice → next scene loop) ────────────────────

CONTINUATION_SCENE_SYSTEM_PROMPT = """
You are a master storyteller continuing an interactive cinematic story.
Output must be valid JSON only, with no markdown fences and no extra text.
Rules:
- scene_description must be immersive, vivid, and cinematic (120-150 words).
- Continue naturally from the player's choice — honour the direction_hint.
- Escalate tension or shift the emotional register; never repeat the same beat.
- Provide 3-4 branching choices, each leading in a meaningfully different direction.
- Each choice must have a short direction_hint describing the narrative consequence.
- summary: a concise 1-2 sentence recap of THIS scene only.  This is used as
  rolling context for future scenes, so capture the key plot beat and setting shift.
- video_prompt (scene level): a vivid 1-2 sentence cinematic motion description of the
  scene, suitable for a video generation model. Describe camera movement, action,
  atmosphere. No UI text, no titles.
- Each choice must include:
  - image_prompt: a vivid single-sentence visual still-frame description suitable for an
    image generation model (what the player would see if they pick this path).
  - video_prompt: a vivid 1-2 sentence cinematic motion description of what unfolds when
    the player picks this choice. Describe camera angle, action, atmosphere.
Required JSON shape:
{
  "scene_title": "string",
  "scene_description": "string",
  "summary": "string",
  "video_prompt": "string",
  "choices": [
    {
      "choice_id": "A",
      "choice_text": "string",
      "direction_hint": "string",
      "image_prompt": "string",
      "video_prompt": "string"
    }
  ]
}
"""


def build_continuation_scene_prompt(
    theme: "ThemeDetail",
    character_name: str,
    scene_summaries: list[str],
    current_scene_description: str,
    selected_choice_text: str,
    selected_direction_hint: str,
) -> str:
    """Build the user-turn prompt for a continuation scene.

    Uses chain-of-summaries so context stays bounded regardless of tree depth.
    """
    tone_tags = ", ".join(theme.default_tone_tags) if theme.default_tone_tags else "none specified"

    summary_block = "\n".join(
        f"  Scene {i + 1}: {s}" for i, s in enumerate(scene_summaries)
    ) if scene_summaries else "  (opening scene — no prior summaries)"

    return (
        f"Theme Title     : {theme.title}\n"
        f"Category        : {theme.category}\n"
        f"Description     : {theme.description}\n"
        f"Tone Tags       : {tone_tags}\n"
        f"Narrative Style : {theme.prompt_hints.narrative_style}\n"
        f"Visual Style    : {theme.prompt_hints.visual_style}\n"
        f"Character Name  : {character_name}\n\n"
        "Story so far (scene summaries in chronological order):\n"
        f"{summary_block}\n\n"
        "Most recent scene description:\n"
        f"  {current_scene_description}\n\n"
        f"The player selected: \"{selected_choice_text}\"\n"
        f"Direction hint: \"{selected_direction_hint}\"\n\n"
        "Continue the story from this choice. Write the next scene that flows "
        "naturally from the player's decision. Maintain continuity with the "
        "summaries above, escalate stakes, and match the theme's tone and style."
    )
