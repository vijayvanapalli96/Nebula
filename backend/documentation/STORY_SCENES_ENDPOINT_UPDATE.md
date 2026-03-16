# Story Scenes Endpoint Update

## Summary
- Added a new authenticated endpoint: `GET /stories/{storyId}/scenes`
- Connected endpoint to Firestore-backed scene retrieval
- Added a clean fallback in-memory repository surface for local/dev behavior
- Added Firestore schema documentation for story scenes
- Added backend unit/route coverage and kept frontend API client aligned

## API Contract
- Route: `GET /stories/{storyId}/scenes`
- Auth: Firebase bearer token required (`require_auth`)
- Response: ordered list of scenes with fields useful for graph + scene playback:
  - IDs and ordering: `scene_id`, `story_id`, `chapter_number`, `scene_number`
  - Narrative text: `title`, `description`, `short_summary`, `full_narrative`
  - Graph lineage: `parent_scene_id`, `selected_choice_id_from_parent`, `path_depth`, `is_root`
  - Progress/ending flags: `is_current_checkpoint`, `is_ending`, `ending_type`
  - Presentation: `scene_type`, `mood`, `location`, `characters_present`
  - Assets and generation states: `asset_refs`, `generation_status`
  - Audit timestamps: `created_at`, `updated_at`

## Firestore Wiring
- Collection path:
  - `/{FIREBASE_STORIES_COLLECTION}/{storyId}/{FIREBASE_SCENES_SUBCOLLECTION}`
- Defaults:
  - `FIREBASE_STORIES_COLLECTION=stories`
  - `FIREBASE_SCENES_SUBCOLLECTION=scenes`
- Scene schema reference:
  - `backend/documentation/scripts/firebase/STORY_SCENES_SCHEMA.md`

## Architectural Changes
- Domain:
  - Added `StorySceneRecord` and nested value objects
  - Added `StorySceneRepository` protocol
- Infrastructure:
  - Added `FirestoreStorySceneRepository`
  - Added `InMemoryStorySceneRepository`
- Application:
  - Added `StorySceneView` DTO family
  - Added `StoryEngineUseCase.list_story_scenes(story_id)`
- Presentation:
  - Added scene response schemas + mapper
  - Added router endpoint `/stories/{storyId}/scenes`

## Frontend API Helper
- Added `fetchStoryScenes(storyId)` in `frontend/src/api/storyApi.ts` for consuming the new endpoint.

## Validation
- Backend: `pytest` => all tests passing
- Frontend: `npm run build` => successful
