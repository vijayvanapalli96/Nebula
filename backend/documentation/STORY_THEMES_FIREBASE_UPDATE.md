# Story Themes + Firebase Integration

## Title
Story Themes Endpoint with Firestore-Backed Theme Catalog

## Summary
- Added `GET /story/themes` endpoint for frontend theme cards.
- Integrated theme retrieval with a Firestore-backed repository.
- Added in-memory fallback for local/dev when Firestore is not configured.
- Added Firestore seed/schema artifacts for initializing theme documents.
- Wired frontend dashboard to fetch themes from backend.

## Backend Changes
- Added `StoryTheme` domain model and `StoryThemeRepository` contract.
- Extended `StoryEngineUseCase` with `list_story_themes()`.
- Added API schema mapper for `StoryThemeResponse`.
- Added repository adapters:
  - `FirestoreStoryThemeRepository`
  - `InMemoryStoryThemeRepository`
- Updated DI wiring to select Firestore when `FIREBASE_PROJECT_ID` is present.
- Added config:
  - `FIREBASE_PROJECT_ID`
  - `FIREBASE_THEMES_COLLECTION`
- Added dependency: `google-cloud-firestore`.

## Firebase Schema Scripts
- Added seed payload JSON:
  - `backend/scripts/firebase/story_themes.seed.json`
- Added seed runner script:
  - `backend/scripts/firebase/seed_story_themes.py`
- Added schema reference:
  - `backend/scripts/firebase/STORY_THEMES_SCHEMA.md`

## Frontend Changes
- Added `fetchStoryThemes()` in `frontend/src/api/storyApi.ts`.
- Dashboard now loads themes from backend and falls back to local defaults on API failure.
- Added store action `setGenres` and exported `FALLBACK_GENRES`.

## Validation
- Backend tests: `cd backend && pytest` (all passing).
- Frontend build: `cd frontend && npm run build` (successful).
