"""
Seed the Firestore `themes` collection with 10 cinematic story themes.

Usage (from the backend/ directory):
    python scripts/seed_themes.py

Uses the active gcloud CLI access token so no separate ADC setup is needed.
Requires: gcloud auth login (already done if you can run gcloud commands).
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2.credentials import Credentials as OAuthCredentials

# ── Firebase init — use gcloud CLI token directly ─────────────────────────

def _gcloud_token() -> str:
    result = subprocess.run(
        "gcloud auth print-access-token",
        capture_output=True, text=True, check=True, shell=True,
    )
    return result.stdout.strip()

_oauth = OAuthCredentials(token=_gcloud_token())
firebase_admin.initialize_app(
    credentials.ApplicationDefault(),  # placeholder; overridden below
    {"projectId": "disclosure-nlu"},
)
# Override the Firestore client to use the gcloud token directly
from google.cloud import firestore as _fs
db = _fs.Client(project="disclosure-nlu", credentials=_oauth)

# ── Theme data ─────────────────────────────────────────────────────────────

NOW = datetime.now(timezone.utc)

THEMES = [
    {
        "themeId": "cyberpunk-noir",
        "title": "Cyberpunk Noir",
        "description": (
            "A neon-drenched megacity drowning in corruption, rogue AI, and "
            "corporate conspiracies. Every flickering hologram hides a lie, "
            "every shadow conceals a mercenary, and the only currency that "
            "matters is leverage."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "sci-fi",
        "defaultToneTags": ["dark", "mysterious", "high-tech", "gritty"],
        "promptHints": {
            "visualStyle": "cinematic neon noir, rain-slicked futuristic streets, holographic ads, lens flares",
            "narrativeStyle": "tense, investigative, morally complex, first-person noir monologue",
        },
        "popularityScore": 100,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "noir-detective",
        "title": "The Last Detective",
        "description": (
            "1940s. Rain-soaked streets, cigarette smoke, and a city that eats "
            "the innocent. You're the only PI willing to take the cases the "
            "police bury. Every dame with sad eyes is a loaded gun, and every "
            "answer unlocks a darker question."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "crime",
        "defaultToneTags": ["gritty", "melancholic", "suspenseful", "cynical"],
        "promptHints": {
            "visualStyle": "black and white noir, deep shadows, rain-soaked alleyways, smoky interiors",
            "narrativeStyle": "hardboiled, sardonic inner monologue, slow-burn mystery reveals",
        },
        "popularityScore": 88,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "fantasy-kingdom",
        "title": "Crown of Ash",
        "description": (
            "A crumbling empire balanced on the edge of a blade. Ancient magic "
            "resurges, noble houses scheme behind silk curtains, and a forgotten "
            "heir must decide whether to save a kingdom that was built on blood "
            "or burn it down to start again."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "fantasy",
        "defaultToneTags": ["epic", "political", "dark-fantasy", "dramatic"],
        "promptHints": {
            "visualStyle": "sweeping medieval landscapes, candlelit throne rooms, decaying grandeur, stormy skies",
            "narrativeStyle": "epic and lyrical, morally ambiguous choices, rich world-building",
        },
        "popularityScore": 92,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "space-exploration",
        "title": "The Outer Drift",
        "description": (
            "Humanity's last colony ship drifts beyond the mapped stars. The "
            "crew is fractured, the AI navigator is behaving strangely, and an "
            "alien signal pulses from a planet that shouldn't exist. First "
            "contact was never supposed to look like this."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "sci-fi",
        "defaultToneTags": ["isolated", "awe-inspiring", "tense", "philosophical"],
        "promptHints": {
            "visualStyle": "vast cosmic vistas, dim spacecraft interiors, alien bioluminescence, deep-space silence",
            "narrativeStyle": "slow-burn dread, existential wonder, crew dynamics under pressure",
        },
        "popularityScore": 85,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "psychological-thriller",
        "title": "Fractured Mind",
        "description": (
            "Reality is unreliable and so is memory. You wake in a white room "
            "with no past and a name that doesn't feel like yours. The doctors "
            "smile too much and the orderly leaves notes under your pillow. "
            "The truth is in your head — if it can be trusted."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "thriller",
        "defaultToneTags": ["unsettling", "surreal", "claustrophobic", "tense"],
        "promptHints": {
            "visualStyle": "clinical whites bleeding into distorted hallways, flickering lights, unreliable flashbacks",
            "narrativeStyle": "unreliable narrator, fragmented memories, escalating paranoia",
        },
        "popularityScore": 90,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "post-apocalyptic",
        "title": "After the Signal",
        "description": (
            "Three years after a signal from the sky silenced every electronic "
            "device on Earth, the survivors have divided into warring factions "
            "across a shattered America. You control a caravan that carries the "
            "only working radio — and everyone wants it."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "post-apocalyptic",
        "defaultToneTags": ["bleak", "survival", "hopeful-undercurrent", "brutal"],
        "promptHints": {
            "visualStyle": "overgrown ruins, harsh sunlight on desolation, makeshift settlements, dust and ash",
            "narrativeStyle": "resource tension, moral trade-offs, community vs. self-preservation",
        },
        "popularityScore": 87,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "political-conspiracy",
        "title": "The Shadow Cabinet",
        "description": (
            "Inside the halls of power, the real decisions are made in "
            "soundproofed rooms by people whose names never appear on ballots. "
            "You've stumbled onto something that could collapse governments — "
            "now three intelligence agencies and one very patient assassin "
            "know your name."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "thriller",
        "defaultToneTags": ["paranoid", "sophisticated", "high-stakes", "intelligent"],
        "promptHints": {
            "visualStyle": "marble corridors, encrypted screens, grey European cities, elegant danger",
            "narrativeStyle": "layered conspiracy, measured dialogue, betrayal at every level",
        },
        "popularityScore": 83,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "supernatural-mystery",
        "title": "What the Dark Keeps",
        "description": (
            "A small coastal town where the fog never fully lifts and the "
            "residents stop making eye contact after dark. A series of "
            "disappearances points to something old that made a deal with the "
            "founders — and the bill is now due."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "horror",
        "defaultToneTags": ["eerie", "atmospheric", "dread", "mystery"],
        "promptHints": {
            "visualStyle": "fog-drenched coastal New England, candlelight, decaying Victorian architecture",
            "narrativeStyle": "slow dread, Lovecraftian unease, community secrets unravelling",
        },
        "popularityScore": 89,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "ancient-mythology",
        "title": "Blood of Olympus",
        "description": (
            "The gods are dying and they're taking the world with them. Mortals "
            "once blessed are now cursed with divine burdens. You carry the "
            "ichor of a forgotten deity and every monster, oracle, and "
            "demigod on the Mediterranean knows your scent."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "mythology",
        "defaultToneTags": ["epic", "mythic", "tragic", "visceral"],
        "promptHints": {
            "visualStyle": "sun-bleached marble ruins, wine-dark seas, divine golden light, blood and laurels",
            "narrativeStyle": "epic tragedy structure, hubris and fate, divine interference in mortal choices",
        },
        "popularityScore": 86,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
    {
        "themeId": "futuristic-rebellion",
        "title": "The Spark Protocol",
        "description": (
            "In 2147, the Collective controls every calorie, every breath of "
            "clean air, every second of bandwidth. You've just received an "
            "encrypted message that proves the system was never designed to "
            "serve humanity — and someone inside the Collective wants it "
            "torn down from within."
        ),
        "thumbnailUrl": "",
        "heroImageUrl": "",
        "category": "sci-fi",
        "defaultToneTags": ["rebellious", "urgent", "dystopian", "idealistic"],
        "promptHints": {
            "visualStyle": "stark brutalist architecture, propaganda screens, hidden underground warmth vs. sterile surfaces",
            "narrativeStyle": "revolutionary urgency, trust and betrayal within resistance cells, escalating stakes",
        },
        "popularityScore": 94,
        "active": True,
        "createdAt": NOW,
        "updatedAt": NOW,
    },
]


# ── Seed function ──────────────────────────────────────────────────────────

def seed_themes() -> None:
    collection = db.collection("themes")
    inserted = 0
    skipped = 0

    for theme in THEMES:
        doc_ref = collection.document(theme["themeId"])
        doc = doc_ref.get()

        if doc.exists:
            print(f"  ⏭  SKIP  {theme['themeId']} (already exists)")
            skipped += 1
        else:
            doc_ref.set(theme)
            print(f"  ✅ INSERT {theme['themeId']}")
            inserted += 1

    print(f"\nDone — {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    print(f"Seeding `themes` collection on project disclosure-nlu …\n")
    seed_themes()
