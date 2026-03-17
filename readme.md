# Interactive Cinematic Story Engine

Interactive Cinematic Story Engine is a full-stack application for AI-driven branching stories.
It includes a React frontend and a FastAPI backend with Gemini-powered story generation, Firebase auth, and Firestore-backed story persistence.

## Repository Layout

| Folder | What it contains |
| --- | --- |
| `frontend/` | React + TypeScript + Vite client app, Firebase auth integration, page-level UI (`src/pages`), API client (`src/api`), and Zustand stores (`src/store`). |
| `backend/` | FastAPI service with layered architecture (`app/presentation`, `app/application`, `app/domain`, `app/infrastructure`), AI adapters, Firestore repositories, and tests. |
| `backend/documentation/` | Backend and frontend documentation, API references, Firestore schema notes, and architecture diagrams. |

## What the Application Does

- Generates themed story setup questions.
- Generates an opening scene and continuation scenes from user choices.
- Persists stories, questions, answers, and scenes in Firestore (with in-memory fallbacks for some flows).
- Supports story media generation paths (images and video), plus creative multimodal composition APIs.
- Provides dashboard-friendly endpoints for a user's story list and full story detail payloads.

## Tech Stack

- Frontend: React 19, TypeScript, Vite, Firebase SDK, Zustand
- Backend: Python 3.11+, FastAPI, Pydantic v2, `google-genai`, Firestore, GCS

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- A Google Gemini API key
- Firebase project config (for auth + Firestore-backed flows)

## Environment Setup

### Backend (`backend/.env`)

```bash
cd backend
cp .env.template .env
```

Minimum values to set:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Common optional values:

```env
# Firestore
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_CREDENTIALS_PATH=/absolute/path/to/service-account.json
FIREBASE_THEMES_COLLECTION=themes
FIREBASE_STORIES_COLLECTION=stories
FIREBASE_SCENES_SUBCOLLECTION=scenes
FIREBASE_USERS_COLLECTION=users
FIREBASE_USER_STORIES_SUBCOLLECTION=stories

# GCS media storage
GCS_BUCKET_NAME=your_bucket
GCS_SA_KEY_PATH=/absolute/path/to/gcs-service-account.json
```

### Frontend (`frontend/.env`)

Create or update `frontend/.env` with:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
VITE_FIREBASE_MEASUREMENT_ID=...
```

## Run Locally (Two Terminals)

### Terminal 1: Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Frontend

```bash
cd frontend
npm install
npm run dev
```

## Local URLs

- Frontend: `http://127.0.0.1:5173`
- Backend API: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

## Useful Commands

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

## Key API Endpoints

- `POST /story/questions`
- `POST /story/opening`
- `POST /story/scene/next`
- `GET /story/media/{story_id}/{scene_id}`
- `GET /stories/me`
- `GET /story/{user_id}/{story_id}`
- `GET /story/themes`
- `GET /stories/{storyId}/scenes`
- `POST /v1/projects`
- `POST /v1/compositions`
- `POST /v1/videos/generate`
- `GET /health`

## Architecture and Detailed Docs

- Backend guide: `backend/documentation/backend/README.md`
- Backend architecture diagrams: `backend/documentation/backend/ARCHITECTURE.md`
