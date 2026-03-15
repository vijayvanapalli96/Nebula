from __future__ import annotations

from app.domain.models.story import StoryTheme
from app.domain.repositories.story_theme_repository import StoryThemeRepository

DEFAULT_THEMES: tuple[StoryTheme, ...] = (
    StoryTheme(
        theme_id="genre-noir",
        title="Noir Detective",
        tagline="Solve a crime in a rain-soaked city.",
        description="Secrets hide in every shadow.\nCan you uncover the truth?",
        image="https://images.unsplash.com/photo-1605806616949-1e87b487fc2f?w=800&q=80",
        accent_color="rgba(234,179,8,0.6)",
        sort_order=10,
    ),
    StoryTheme(
        theme_id="genre-scifi",
        title="Sci-Fi Exploration",
        tagline="Discover secrets beyond the stars.",
        description="The cosmos holds answers.\nDare to ask the questions.",
        image="https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&q=80",
        accent_color="rgba(59,130,246,0.6)",
        sort_order=20,
    ),
    StoryTheme(
        theme_id="genre-thriller",
        title="Psychological Thriller",
        tagline="Reality may not be what it seems.",
        description="Your mind is both prison and key.\nTrust nothing.",
        image="https://images.unsplash.com/photo-1518895312237-a9e23508077d?w=800&q=80",
        accent_color="rgba(239,68,68,0.6)",
        sort_order=30,
    ),
    StoryTheme(
        theme_id="genre-fantasy",
        title="Fantasy Kingdom",
        tagline="Magic, politics, and ancient power.",
        description="A throne of lies. A destiny of fire.\nRise or be forgotten.",
        image="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80",
        accent_color="rgba(168,85,247,0.6)",
        sort_order=40,
    ),
    StoryTheme(
        theme_id="genre-apocalyptic",
        title="Post-Apocalyptic",
        tagline="Survive a ruined world.",
        description="The old world is ash.\nYour choices write the new one.",
        image="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        accent_color="rgba(249,115,22,0.6)",
        sort_order=50,
    ),
    StoryTheme(
        theme_id="genre-political",
        title="Political Conspiracy",
        tagline="Truth is buried beneath power.",
        description="Everyone has an agenda.\nOnly you can expose it.",
        image="https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80",
        accent_color="rgba(20,184,166,0.6)",
        sort_order=60,
    ),
)


class InMemoryStoryThemeRepository(StoryThemeRepository):
    def __init__(self, themes: list[StoryTheme] | None = None) -> None:
        self._themes = list(themes) if themes is not None else list(DEFAULT_THEMES)

    def list_active(self) -> list[StoryTheme]:
        return sorted(
            [theme for theme in self._themes if theme.is_active],
            key=lambda theme: theme.sort_order,
        )
