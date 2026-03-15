from __future__ import annotations

from app.domain.models.story import HistoryEntry, SceneChoice, StoryState

INITIAL_QUESTIONS_SYSTEM_PROMPT = """
You are an AI creative director designing an interactive story.
Output must be valid JSON only, with no markdown fences and no extra text.
Rules:
- Questions must be abstract and creative.
- Each question must have exactly 4 answer options.
- Avoid complicated wording.
- The answers should influence tone, motivation, or world style.
Required JSON shape:
{
  "questions": [
    {
      "question": "string",
      "options": ["string", "string", "string", "string"]
    }
  ]
}
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

