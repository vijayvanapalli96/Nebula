# Nebula Backend Architecture

Generated from current backend code (`backend/app/*`) on `main`.

## 1) Backend Runtime Architecture

```mermaid
flowchart LR
  subgraph Clients
    FE[Frontend Web App]
    DEV[Developer or QA via Swagger]
  end

  subgraph Backend[FastAPI Backend]
    APP[app/main.py create_app]
    AUTH[require_auth dependency]
    R1[Story Router<br/>router.py]
    R2[Creative Router<br/>creative_router.py]
    R3[Video Router<br/>video_router.py]
    R4[User Router<br/>user_router.py]
  end

  subgraph AppLayer[Application Use Cases]
    U1[StoryEngineUseCase]
    U2[GenerateStoryQuestionsUseCase]
    U3[CreativeStorytellingUseCase]
    U4[VideoGenerationUseCase]
    U5[GetThemeUseCase]
    U6[CreateStoryUseCase]
  end

  subgraph Ports[Ports]
    P1[StoryGeneratorPort]
    P2[ThemedQuestionGeneratorPort]
    P3[InterleavedGeneratorPort]
    P4[VideoGeneratorPort]
    P5[ImageStoragePort]
  end

  subgraph Adapters[Infrastructure Adapters]
    A1[GeminiStoryGenerator]
    A2[GeminiThemedQuestionGenerator]
    A3[GeminiInterleavedGenerator]
    A4[GeminiVideoGenerator]
    A5[GcsImageStorage]
    DB1[Firestore repositories]
    DB2[In-memory repositories]
  end

  subgraph External[External Systems]
    FA[Firebase Auth]
    FS[Google Firestore]
    GCS[Google Cloud Storage]
    GEM[Gemini API]
    VEO[Veo model]
    LFS[(generated_videos/*.mp4)]
  end

  FE -->|Bearer token| APP
  DEV --> APP
  APP --> AUTH
  AUTH --> FA
  APP --> R1
  APP --> R2
  APP --> R3
  APP --> R4

  R1 --> U1
  R1 --> U2
  U2 --> U5
  U2 --> U6
  R2 --> U3
  R3 --> U4
  R4 --> FS

  U1 --> P1
  U1 --> P4
  U1 --> P5
  U2 --> P1
  U2 --> P2
  U2 --> P5
  U3 --> P3
  U4 --> P4

  P1 --> A1
  P2 --> A2
  P3 --> A3
  P4 --> A4
  P5 --> A5

  A1 --> GEM
  A2 --> GEM
  A3 --> GEM
  A4 --> VEO
  A5 --> GCS

  U1 --> DB1
  U2 --> DB1
  U3 --> DB2
  U4 --> DB2
  DB1 --> FS
  U4 --> LFS
```

## 2) Internal Layering (Hexagonal)

```mermaid
flowchart TB
  subgraph Presentation[Presentation Layer]
    PR1[router.py]
    PR2[creative_router.py]
    PR3[video_router.py]
    PR4[user_router.py]
    SCH[schemas.py + creative_schemas.py + video_schemas.py]
    DEP[dependencies.py DI wiring]
  end

  subgraph Application[Application Layer]
    UC1[story_engine.py]
    UC2[generate_story_questions.py]
    UC3[creative_storytelling.py]
    UC4[video_generation.py]
    UC5[get_theme.py]
    UC6[create_story.py]
    DTO[dto/* commands and results]
    PORTS[ports/*]
  end

  subgraph Domain[Domain Layer]
    MODELS[domain/models/*]
    REPOS[domain/repositories/* protocols]
  end

  subgraph Infrastructure[Infrastructure Layer]
    AI[infrastructure/ai/*]
    FIRE[infrastructure/repositories/firestore_*]
    MEM[infrastructure/repositories/in_memory_*]
    STORE[infrastructure/storage/gcs_image_storage.py]
    FBADMIN[infrastructure/firebase/admin.py]
  end

  SCH --> PR1
  SCH --> PR2
  SCH --> PR3
  DEP --> PR1
  DEP --> PR2
  DEP --> PR3
  DEP --> PR4

  PR1 --> UC1
  PR1 --> UC2
  PR2 --> UC3
  PR3 --> UC4

  UC1 --> DTO
  UC2 --> DTO
  UC3 --> DTO
  UC4 --> DTO

  UC1 --> PORTS
  UC2 --> PORTS
  UC3 --> PORTS
  UC4 --> PORTS
  UC5 --> REPOS
  UC6 --> REPOS

  UC1 --> REPOS
  UC2 --> REPOS
  UC3 --> REPOS
  UC4 --> REPOS
  REPOS --> MODELS

  PORTS --> AI
  PORTS --> STORE
  REPOS --> FIRE
  REPOS --> MEM
  FBADMIN --> FIRE
```

## 3) Firestore Data Model Used by Story Endpoints

```mermaid
flowchart TD
  FS[(Firestore)]

  FS --> USERS[users]
  USERS --> UID["{uid}"]
  UID --> USTORIES["stories/{story_id}"]
  USTORIES --> Q["questions/{question_id}"]
  USTORIES --> A["answers/{question_id}"]
  USTORIES --> S["scenes/{scene_id}"]

  FS --> THEMES["themes/{theme_id}"]

  FS --> STORIES["stories/{storyId}"]
  STORIES --> STORY_SCENES["scenes/{scene_id}"]

  USTORIES --> META["story metadata fields<br/>status, theme*, rootSceneId, branchDepth,<br/>characterName, customInput, updatedAt"]
```

## 4) Sequence: `GET /story/{user_id}/{story_id}`

This endpoint returns story metadata plus raw `questions`, `answers`, and `scenes`.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant API as router.py
  participant AUTH as require_auth
  participant UC as StoryEngineUseCase
  participant USERREP as UserStoryRepository
  participant DOCREP as StoryDocumentRepository
  participant FS as Firestore

  FE->>API: GET /story/{user_id}/{story_id}
  API->>AUTH: verify Bearer token
  AUTH-->>API: token_uid
  API->>API: enforce token_uid == user_id
  API->>UC: get_story_detail(user_id, story_id)
  UC->>USERREP: get_by_story_id(user_id, story_id)
  USERREP->>FS: read users/{uid}/stories/{story_id}
  FS-->>USERREP: story card record
  UC->>DOCREP: get_story_payload(user_id, story_id)
  DOCREP->>FS: read subcollections questions/answers/scenes
  FS-->>DOCREP: raw payload docs
  UC-->>API: StoryDetailView + payload
  API-->>FE: StoryDetailResponse
```

## Current Media Status

- Story flow supports image and video asset URLs per choice (`/story/media/{story_id}/{scene_id}`).
- Dedicated video generation exists at `/v1/videos/*` and writes output to `generated_videos/`.
- Creative composition supports requested modalities including `audio` and `video`; current interleaved generator emits queued placeholders for modalities not directly generated in-line.
