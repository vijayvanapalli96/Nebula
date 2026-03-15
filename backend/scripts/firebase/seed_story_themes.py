from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from google.cloud import firestore


def _load_seed_file(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    themes = payload.get("themes")
    if not isinstance(themes, list):
        raise ValueError("Seed file must contain a top-level 'themes' list.")
    return themes


def _normalize_theme(theme: dict[str, Any], index: int) -> tuple[str, dict[str, Any]]:
    theme_id = str(theme.get("id", "")).strip()
    if not theme_id:
        raise ValueError(f"Theme at index {index} is missing a non-empty 'id'.")

    required_fields = ("title", "tagline", "description", "image", "accent_color")
    normalized = {
        "title": str(theme.get("title", "")).strip(),
        "tagline": str(theme.get("tagline", "")).strip(),
        "description": str(theme.get("description", "")).strip(),
        "image": str(theme.get("image", "")).strip(),
        "accent_color": str(theme.get("accent_color", "")).strip(),
        "is_active": bool(theme.get("is_active", True)),
        "sort_order": int(theme.get("sort_order", (index + 1) * 10)),
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    missing = [field for field in required_fields if not normalized[field]]
    if missing:
        raise ValueError(
            f"Theme '{theme_id}' has empty required fields: {', '.join(missing)}."
        )

    return theme_id, normalized


def seed_story_themes(
    project_id: str,
    collection_name: str,
    seed_file: Path,
) -> None:
    client = firestore.Client(project=project_id)
    themes = _load_seed_file(seed_file)

    batch = client.batch()
    collection = client.collection(collection_name)
    count = 0
    for index, theme in enumerate(themes):
        theme_id, payload = _normalize_theme(theme, index)
        batch.set(collection.document(theme_id), payload, merge=True)
        count += 1

    batch.commit()
    print(
        f"Seeded {count} story themes into collection '{collection_name}' "
        f"(project: {project_id}).",
    )


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    default_seed_file = script_dir / "story_themes.seed.json"
    default_project_id = os.getenv("FIREBASE_PROJECT_ID", "")

    parser = argparse.ArgumentParser(
        description="Seed Firestore story themes collection.",
    )
    parser.add_argument(
        "--project-id",
        default=default_project_id,
        help="GCP project id containing the Firestore database.",
    )
    parser.add_argument(
        "--collection",
        default="themes",
        help="Firestore collection name (default: themes).",
    )
    parser.add_argument(
        "--seed-file",
        default=str(default_seed_file),
        help="Path to JSON file with themes payload.",
    )
    args = parser.parse_args()
    if not args.project_id:
        parser.error(
            "--project-id is required (or set FIREBASE_PROJECT_ID in environment).",
        )
    return args


if __name__ == "__main__":
    args = parse_args()
    seed_story_themes(
        project_id=args.project_id,
        collection_name=args.collection,
        seed_file=Path(args.seed_file),
    )
