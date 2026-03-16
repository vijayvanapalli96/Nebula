# User Stories Firestore Schema (`/stories/me`, `/story/{user_id}/{story_id}`)

Endpoints:

- `GET /stories/me` (authenticated)
- `GET /story/{user_id}/{story_id}` (authenticated, `token_uid == user_id`)

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
  "userId": "uid_123",
  "sessionId": "session_123",
  "title": "Crimson Echoes",
  "themeTitle": "Crimson Echoes",
  "themeId": "theme_crime",
  "genre": "Noir",
  "themeCategory": "Noir",
  "themeDescription": "A rain-soaked detective arc.",
  "characterName": "Kira Voss",
  "archetype": "Detective",
  "lastSceneId": "scene_010",
  "questionCount": 4,
  "questionsGenerated": ["Q1", "Q2", "Q3", "Q4"],
  "choicesAvailable": 3,
  "progress": 62,
  "coverImage": "https://.../cover.jpg",
  "status": "active",
  "createdAt": "timestamp",
  "lastPlayedAt": "timestamp",
  "updatedAt": "timestamp"
}
```

## Supported key variants

The backend mapper is tolerant to common variants:

- `storyId|story_id`
- `userId|user_id`
- `sessionId|session_id`
- `title|storyTitle|name|themeTitle`
- `genre|theme|category|themeCategory`
- `themeId|theme_id`
- `themeDescription|theme_description|description`
- `characterName|character_name|heroName|protagonistName`
- `archetype|characterArchetype`
- `lastSceneId|last_scene_id|currentSceneId|current_scene_id`
- `choicesAvailable|choices_available|availableChoices`
- `questionCount|question_count`
- `questionsGenerated|questions_generated`
- `progress|progressPercent`
- `coverImage|cover_image|thumbnailUrl|heroImageUrl`
- `status`
- `createdAt|created_at`
- `lastPlayedAt|last_played_at`
- `updatedAt|updated_at`

## Response model fields

`/stories/me` returns:

- `story_id`, `session_id`, `title`, `genre`, `character_name`, `archetype`
- `last_scene_id`, `updated_at`, `choices_available`
- `progress`, `cover_image`, `last_played_at`, `status`

`/story/{user_id}/{story_id}` returns everything above plus:

- `user_id`
- `theme_id`, `theme_title`, `theme_category`, `theme_description`
- `question_count`, `questions_generated`
- `created_at`
