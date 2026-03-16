# User Stories Firestore Schema (`/stories/me`)

Endpoint:

- `GET /stories/me` (authenticated)

Primary Firestore path:

- `/{FIREBASE_USERS_COLLECTION}/{uid}/{FIREBASE_USER_STORIES_SUBCOLLECTION}`
- Defaults:
  - `FIREBASE_USERS_COLLECTION=users`
  - `FIREBASE_USER_STORIES_SUBCOLLECTION=stories`

## Recommended document shape

Document id can be the story id.

```json
{
  "storyId": "story_123",
  "sessionId": "session_123",
  "title": "Crimson Echoes",
  "themeTitle": "Crimson Echoes",
  "genre": "Noir",
  "themeCategory": "Noir",
  "characterName": "Kira Voss",
  "archetype": "Detective",
  "lastSceneId": "scene_010",
  "choicesAvailable": 3,
  "progress": 62,
  "coverImage": "https://.../cover.jpg",
  "status": "active",
  "lastPlayedAt": "timestamp",
  "updatedAt": "timestamp"
}
```

## Supported key variants

The backend mapper is tolerant to common variants:

- `storyId|story_id`
- `sessionId|session_id`
- `title|storyTitle|name`
- `title|storyTitle|name|themeTitle`
- `genre|theme|category|themeCategory`
- `characterName|character_name|heroName|protagonistName`
- `archetype|characterArchetype`
- `lastSceneId|last_scene_id|currentSceneId|current_scene_id`
- `choicesAvailable|choices_available|availableChoices`
- `progress|progressPercent`
- `coverImage|cover_image|thumbnailUrl|heroImageUrl`
- `status`
- `lastPlayedAt|last_played_at`
- `updatedAt|updated_at`

## Response model fields

`/stories/me` returns:

- `story_id`, `session_id`, `title`, `genre`, `character_name`, `archetype`
- `last_scene_id`, `updated_at`, `choices_available`
- `progress`, `cover_image`, `last_played_at`, `status`
