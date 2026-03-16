# User Stories Endpoint Update

## Goal

Update `GET /stories/me` to read stories from Firestore user scope:

- `users/{uid}/stories`

Add story-detail endpoint:

- `GET /story/{user_id}/{story_id}`

## What Changed

- Added `UserStoryRepository` domain port.
- Added `FirestoreUserStoryRepository` adapter.
- Wired repository through DI and `StoryEngineUseCase`.
- Updated `GET /stories/me` to pass authenticated UID into `list_active_stories(user_id)`.
- Added `GET /story/{user_id}/{story_id}` to return full story info for one story.
- Expanded response payload for frontend utility:
  - `story_id`
  - `progress`
  - `cover_image`
  - `last_played_at`
  - `status`
  - `theme_id`, `theme_title`, `theme_category`, `theme_description`
  - `question_count`, `questions_generated`, `created_at`
- Added Firebase schema doc:
  - `documentation/scripts/firebase/USER_STORIES_SCHEMA.md`

## Live Firestore Check (project: `disclosure-nlu`)

Checked user `tmduUAxT4nNHLQDWmKsb9bf58342` in:

- `users/tmduUAxT4nNHLQDWmKsb9bf58342/stories`

Current data observed during implementation:

- Document count: `6` (as of March 16, 2026)
- Keys in docs include:
  - `storyId`
  - `themeTitle`
  - `themeCategory`
  - `questionCount`
  - `status`
  - `createdAt`
  - `updatedAt`
  - `userId`

Mapper now supports these keys directly.

## Tests

- Added `test_firestore_user_story_repository.py`
- Updated route/use-case tests
- Added route tests for `/story/{user_id}/{story_id}` (200/403/404)
- Full backend test suite passes (`40` tests)
