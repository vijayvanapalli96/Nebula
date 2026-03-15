"""
scripts/seed_themes.py
──────────────────────
Seed the Firestore `themes` collection with 10 cinematic storytelling worlds.

Run from the backend/ directory:

    python -m scripts.seed_themes

Behaviour:
  - Uses `set(..., merge=True)` so existing documents are NEVER overwritten.
  - Existing themes are skipped (logged, not silently ignored).
  - Dry-run support: pass --dry-run to print what *would* be inserted.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from typing import Any

# ── Bootstrap: reuse the existing Firebase Admin singleton ─────────────────
# Running as `python -m scripts.seed_themes` from backend/ ensures the
# `app` package is on sys.path.
from app.infrastructure.firebase.admin import get_db

# ── Theme data ─────────────────────────────────────────────────────────────

NOW = datetime.now(timezone.utc)

THEMES: list[dict[str, Any]] = [
    {
        "themeId": "cyberpunk-noir",
        "title": "Cyberpunk Noir",
        "description": (
            "A neon-drenched megacity choked with corporate espionage, rogue AI, "
            "and underground resistance. Every rain-slicked alley conceals a deal "
            "gone wrong — and the line between human and machine is the last moral "
            "boundary left."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "sci-fi",
        "defaultToneTags": ["dark", "mysterious", "high-tech", "gritty"],
        "promptHints": {
            "visualStyle": "cinematic neon noir, rain-soaked futuristic cityscapes, lens flares, deep shadows",
            "narrativeStyle": "tense, investigative, morally complex, first-person internal monologue",
        },
        "popularityScore": 100,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "noir-detective",
        "title": "Noir Detective",
        "description": (
            "Post-war shadows fall long across a city rotting from the inside. "
            "A world-weary detective takes cases that the law won't touch, "
            "navigating corruption, femmes fatales, and buried secrets that "
            "powerful people will kill to keep."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "mystery",
        "defaultToneTags": ["cynical", "atmospheric", "suspenseful", "moody"],
        "promptHints": {
            "visualStyle": "black-and-white film grain, hard shadows, smoke-filled offices, wet cobblestones",
            "narrativeStyle": "hard-boiled voiceover, fatalistic tone, sharp dialogue, slow-burn reveals",
        },
        "popularityScore": 88,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "fantasy-kingdom",
        "title": "Fantasy Kingdom",
        "description": (
            "Throne rooms and battlefields, bloodlines and betrayals. An ancient "
            "kingdom fractures as old alliances crumble and a forgotten power stirs "
            "in the deep forests. Magic is real — and it demands a price only the "
            "willing can pay."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "fantasy",
        "defaultToneTags": ["epic", "political", "mythic", "dangerous"],
        "promptHints": {
            "visualStyle": "painterly high fantasy, torchlit castles, sweeping landscapes, rich heraldic colors",
            "narrativeStyle": "epic omniscient narration, courtly dialogue, high stakes, multi-faction intrigue",
        },
        "popularityScore": 92,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "space-exploration",
        "title": "Space Exploration",
        "description": (
            "Beyond the last charted star, a lone crew pushes into the unknown. "
            "First contact, dying suns, and the terrifying silence between worlds. "
            "The universe is vast, indifferent — and something out there has been "
            "waiting a very long time."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "sci-fi",
        "defaultToneTags": ["awe-inspiring", "lonely", "tense", "philosophical"],
        "promptHints": {
            "visualStyle": "hard sci-fi cinematography, deep-space vistas, bioluminescent alien worlds, stark spacecraft interiors",
            "narrativeStyle": "slow-burn discovery, crew dynamics, existential stakes, scientific realism with cosmic horror undertones",
        },
        "popularityScore": 85,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "psychological-thriller",
        "title": "Psychological Thriller",
        "description": (
            "Reality frays at the edges. Memory cannot be trusted, and the greatest "
            "threat may already be inside your own mind. A character study of obsession, "
            "identity, and the terrifying cost of knowing the truth."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "thriller",
        "defaultToneTags": ["paranoid", "unsettling", "cerebral", "claustrophobic"],
        "promptHints": {
            "visualStyle": "desaturated palette with jarring color intrusions, distorted angles, fractured mirrors, clinical environments",
            "narrativeStyle": "unreliable narrator, escalating dread, fragmented timelines, sharp psychological reveals",
        },
        "popularityScore": 90,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "post-apocalyptic",
        "title": "Post-Apocalyptic",
        "description": (
            "Civilisation ended forty years ago. The survivors built something new "
            "from the wreckage — brutal, tribal, and fragile. In the wasteland, "
            "every resource is a reason to fight and every stranger is either a "
            "potential ally or your next enemy."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "sci-fi",
        "defaultToneTags": ["bleak", "survival", "hopeful-undercurrent", "violent"],
        "promptHints": {
            "visualStyle": "dust-soaked golden hour, rusted infrastructure, makeshift settlements, scorched horizons",
            "narrativeStyle": "survival-focused, morally grey characters, found-family dynamics, sparse haunting prose",
        },
        "popularityScore": 87,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "political-conspiracy",
        "title": "Political Conspiracy",
        "description": (
            "Behind every election, every war, every crisis — a shadow network "
            "pulling the strings. An investigator stumbles onto a thread that "
            "unravels decades of carefully constructed lies, putting everyone they "
            "love in the crosshairs of the state."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "thriller",
        "defaultToneTags": ["paranoid", "intelligent", "high-stakes", "morally-complex"],
        "promptHints": {
            "visualStyle": "clean modernist architecture with oppressive scale, CCTV aesthetics, hushed back-rooms, coded documents",
            "narrativeStyle": "layered dialogue with hidden meaning, escalating stakes, institutional menace, journalistic precision",
        },
        "popularityScore": 83,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "supernatural-mystery",
        "title": "Supernatural Mystery",
        "description": (
            "A quiet coastal town. Three disappearances in thirty years, all on the "
            "same night. The official explanation never made sense — and now you are "
            "here, and the town is watching. Something old has woken up, and it "
            "remembers you."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "horror",
        "defaultToneTags": ["eerie", "folkloric", "slow-burn", "dread"],
        "promptHints": {
            "visualStyle": "muted coastal palette, fog, practical lighting, decayed Victorian architecture, liminal spaces",
            "narrativeStyle": "atmospheric dread, unreliable locals, escalating weirdness, Gothic sensibility with modern grounding",
        },
        "popularityScore": 89,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "ancient-mythology",
        "title": "Ancient Mythology",
        "description": (
            "The age of heroes has ended — or so the gods would have you believe. "
            "Born of divine blood and mortal ambition, you walk a world where "
            "monsters are real, oracles speak truth wrapped in riddles, and the "
            "Olympians play chess with human lives."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "fantasy",
        "defaultToneTags": ["epic", "fatalistic", "divine", "brutal"],
        "promptHints": {
            "visualStyle": "sun-bleached marble, wine-dark seas, Mediterranean light, divine radiance contrasted with mortal grit",
            "narrativeStyle": "heroic epic register, fate and free will tension, divine intervention, tragic arc potential",
        },
        "popularityScore": 86,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "futuristic-rebellion",
        "title": "Futuristic Rebellion",
        "description": (
            "A gleaming utopia built on invisible chains. The lower tiers have had "
            "enough. A movement born in encrypted messages and back-channel meetings "
            "is about to ignite — and the system's counter-response will be swift, "
            "ruthless, and total."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "sci-fi",
        "defaultToneTags": ["revolutionary", "urgent", "tech-dystopian", "collectivist"],
        "promptHints": {
            "visualStyle": "stark contrast between gleaming elite towers and grimy industrial lower districts, protest iconography, propaganda aesthetics",
            "narrativeStyle": "ensemble cast, ideological tension, sacrifice and betrayal, momentum-driven pacing",
        },
        "popularityScore": 84,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
]

# ── Seed function ──────────────────────────────────────────────────────────


def seed_themes(*, dry_run: bool = False) -> None:
    """
    Insert theme documents into Firestore.

    Uses ``set(..., merge=True)`` which means:
      - New documents are created in full.
      - Existing documents have only the provided fields merged — no data loss.

    If you want a hard reset instead, replace with ``.set(theme)`` (no merge).
    """
    db = get_db()
    collection = db.collection("themes")

    inserted = 0
    skipped = 0

    for theme in THEMES:
        theme_id: str = theme["themeId"]
        ref = collection.document(theme_id)

        if dry_run:
            print(f"  [DRY-RUN] Would upsert → themes/{theme_id}")
            inserted += 1
            continue

        # Check existence so we can log skip vs insert clearly.
        snapshot = ref.get()
        if snapshot.exists:
            print(f"  SKIP   themes/{theme_id}  (already exists)")
            skipped += 1
        else:
            ref.set(theme, merge=True)
            print(f"  INSERT themes/{theme_id}  ✓")
            inserted += 1

    print()
    if dry_run:
        print(f"Dry-run complete. Would insert {inserted} theme(s).")
    else:
        print(f"Done. Inserted: {inserted}  |  Skipped: {skipped}  |  Total: {len(THEMES)}")


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Firestore themes collection.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be inserted without touching Firestore.",
    )
    args = parser.parse_args()

    print(f"\nSeeding {len(THEMES)} themes into Firestore collection `themes`…\n")
    try:
        seed_themes(dry_run=args.dry_run)
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
