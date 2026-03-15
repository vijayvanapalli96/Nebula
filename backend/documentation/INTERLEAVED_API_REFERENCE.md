# Interleaved API Reference

This document captures the multimodal `/v1` API changes implemented on branch `feature/interleaved-api`.

## Scope

- Add high-level creative storytelling APIs with interleaved/mixed output support.
- Keep clean architecture layering (`domain`, `application`, `infrastructure`, `presentation`).
- Provide in-memory implementations for MVP behavior.

## New API Endpoints

### `POST /v1/projects`

Creates a reusable creative project.

- Input: `title`, `use_case`, optional `tone`, `style_bible`
- Output: `project_id`, metadata timestamps, saved style configuration

### `POST /v1/compositions`

Creates a multimodal composition from a prompt.

- Input: `prompt`, `target_platform`, optional `project_id`, `requested_modalities`, `max_parts`
- Output: composition snapshot with ordered `parts[]`, `status`, `usage`

### `GET /v1/compositions/{composition_id}`

Returns full composition state including parts and usage.

### `GET /v1/compositions/{composition_id}/stream`

Streams composition events via SSE (`text/event-stream`).

Current event shapes:

- `composition_status`: `<composition_id>|<status>|v<version>`
- `part`: `<part_id>|<type>|<status>|<content_or_uri>`
- `done`: `<composition_id>`

### `PATCH /v1/compositions/{composition_id}/parts/{part_id}`

Regenerates a single part without rebuilding the full composition.

- Input: optional `instruction`
- Output: updated composition with incremented `version`

### `POST /v1/assets:upload-url`

Creates a temporary upload descriptor for client-side asset upload.

- Output includes `upload_url`, `storage_uri`, `expires_at`

### `GET /v1/assets/{asset_id}`

Fetches stored asset metadata.

### `POST /v1/compositions/{composition_id}:export`

Creates export descriptor for a composition.

- Input: `export_format` (e.g. `json`, `zip`)
- Output: `download_url`, `expires_at`

### `GET /v1/usage`

Returns aggregate usage counters across generated compositions.

## Data Model Additions

Implemented in `app/domain/models/composition.py`:

- `Project`
- `Composition`
- `CompositionPart`
- `AssetRecord`
- `GenerationUsage`

Key enums/literals:

- Part type: `text | image | audio | video | caption | cta`
- Part status: `queued | generating | completed | failed`
- Composition status: `queued | generating | partial | completed | failed`

## Application Layer Additions

- Commands: `creative_commands.py`
- Result DTO: `creative_results.py`
- Port: `interleaved_generator.py`
- Use case: `creative_storytelling.py`
- Errors extended in `application/errors.py`:
  - `ProjectNotFoundError`
  - `CompositionNotFoundError`
  - `PartNotFoundError`
  - `AssetNotFoundError`

## Infrastructure Layer Additions

### AI Adapter

`app/infrastructure/ai/gemini_interleaved_generator.py`

- Uses `google-genai` async client.
- Sends interleaved generation requests.
- Maps Gemini response parts into `CompositionPart` entities.
- Adds placeholder parts for requested modalities not returned immediately (audio/video queued).

### Repositories

`app/infrastructure/repositories/in_memory_creative_repository.py`

- In-memory workspace store for:
  - projects
  - compositions
  - assets
  - usage counters
- Provides typed adapters for each repository contract.

## Presentation Layer Additions

- Schemas: `app/presentation/api/creative_schemas.py`
- Router: `app/presentation/api/creative_router.py`
- Dependency wiring: extended `app/presentation/api/dependencies.py`
- App wiring: `app/main.py` includes `creative_router`

## Tests Added

- `tests/test_creative_routes.py`
- `tests/test_creative_use_case.py`

Current suite status after changes:

- `12 passed` with `pytest -q`

## Known MVP Limitations

- Storage is in-memory only; all creative data resets on process restart.
- Upload/export URLs are mock descriptors (no real signed URL integration yet).
- Audio/video are represented as queued placeholders unless downstream render workers are added.

## Suggested Next Production Steps

1. Replace in-memory creative repositories with Firestore/Redis + Cloud Storage integration.
2. Add auth and tenant scoping for projects/compositions/assets.
3. Add async job orchestration for audio/video rendering (Cloud Tasks or Pub/Sub).
4. Add response contracts for richer SSE payloads (JSON event data instead of delimited strings).
5. Add integration tests for Gemini and cloud-storage workflows.

