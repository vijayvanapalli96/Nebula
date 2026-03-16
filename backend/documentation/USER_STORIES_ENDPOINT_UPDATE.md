# User Stories Endpoint Update

## Goal

Update `GET /stories/me` to read stories from Firestore user scope:

- `users/{uid}/stories`

## What Changed

- Added `UserStoryRepository` domain port.
- Added `FirestoreUserStoryRepository` adapter.
- Wired repository through DI and `StoryEngineUseCase`.
- Updated `GET /stories/me` to pass authenticated UID into `list_active_stories(user_id)`.
- Expanded response payload for frontend utility:
  - `story_id`
  - `progress`
  - `cover_image`
  - `last_played_at`
  - `status`
- Added Firebase schema doc:
  - `documentation/scripts/firebase/USER_STORIES_SCHEMA.md`

## Live Firestore Check (project: `disclosure-nlu`)

Checked user `tmduUAxT4nNHLQDWmKsb9bf58342` in:

- `users/tmduUAxT4nNHLQDWmKsb9bf58342/stories`

Current data observed during implementation:

- Document count: `4`
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
- Full backend test suite passes
