# Firestore Story Themes Schema

Collection: `story_themes` (configurable via `FIREBASE_THEMES_COLLECTION`)

Document ID:
- `id` from the seed payload (for example: `genre-noir`)

Required fields:
- `title` (string)
- `tagline` (string)
- `description` (string)
- `image` (string URL)
- `accent_color` (string, CSS color)

Optional fields:
- `is_active` (boolean, default `true`)
- `sort_order` (integer, default by insertion order)
- `updated_at` (timestamp, set by seed script)

Seed command:

```bash
python scripts/firebase/seed_story_themes.py \
  --project-id YOUR_GCP_PROJECT_ID \
  --collection story_themes
```
