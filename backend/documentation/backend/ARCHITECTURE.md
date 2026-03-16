# Nebula Architecture Diagram

This diagram is generated from the current code under `backend/app/*`, including existing video capabilities and the planned audio output path.

## 1) Whole Application Architecture (Current + Near-Term)

```mermaid
flowchart LR
  %% Clients
  U[End User]
  FE[React Frontend<br/>Vite + Firebase Auth]

  %% Backend entrypoint
  API[FastAPI App<br/>app/main.py]
  AUTH[Auth Guard<br/>require_auth]

  %% Routers
  R1[Story Router<br/>/story/* /stories/*]
  R2[Creative Router<br/>/v1/*]
  R3[Video Router<br/>/v1/videos/*]
  R4[User Router<br/>/api/users/create]

  %% Use cases
  UC1[StoryEngineUseCase]
  UC2[GenerateStoryQuestionsUseCase]
  UC3[CreativeStorytellingUseCase]
  UC4[VideoGenerationUseCase]

  %% Ports / adapters
  P1[StoryGeneratorPort]
  P2[ThemedQuestionGeneratorPort]
  P3[InterleavedGeneratorPort]
  P4[VideoGeneratorPort]
  P5[ImageStoragePort]

  A1[GeminiStoryGenerator]
  A2[GeminiThemedQuestionGenerator]
  A3[GeminiInterleavedGenerator]
  A4[GeminiVideoGenerator]
  A5[GcsImageStorage]

  %% Repositories
  REP1[FirestoreStoryDocumentRepository]
  REP2[FirestoreUserStoryRepository]
  REP3[FirestoreStorySceneRepository]
  REP4[FirestoreStoryThemeRepository]
  REP5[FirestoreThemeDetailRepository]
  REP6[InMemory Repositories<br/>fallback + creative/video stores]

  %% External systems
  FB[Firebase Auth]
  FS[Google Firestore]
  GCS[Google Cloud Storage]
  GEM[Google Gemini APIs]
  VEO[Veo Video Model]
  LF[(Local Filesystem<br/>generated_videos/)]

  U --> FE
  FE -->|Bearer ID Token| API
  FE -->|Sign-in| FB

  API --> AUTH
  AUTH -->|verify token| FB

  API --> R1
  API --> R2
  API --> R3
  API --> R4

  R1 --> UC1
  R1 --> UC2
  R2 --> UC3
  R3 --> UC4
  R4 --> FS

  UC1 --> P1
  UC2 --> P1
  UC2 --> P2
  UC3 --> P3
  UC1 --> P4
  UC4 --> P4
  UC1 --> P5
  UC2 --> P5

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

  UC1 --> REP1
  UC1 --> REP2
  UC1 --> REP3
  UC1 --> REP4
  UC2 --> REP1
  UC2 --> REP5
  UC4 --> REP6
  UC3 --> REP6

  REP1 --> FS
  REP2 --> FS
  REP3 --> FS
  REP4 --> FS
  REP5 --> FS
  UC4 --> LF
```

## 2) Backend Internal Layering (Hexagonal Style)

```mermaid
flowchart TB
  subgraph Presentation["Presentation Layer (FastAPI Routers + Schemas)"]
    PR1[router.py]
    PR2[creative_router.py]
    PR3[video_router.py]
    PR4[user_router.py]
    SCH[schemas.py / creative_schemas.py / video_schemas.py]
  end

  subgraph Application["Application Layer (Use Cases + Ports + DTOs)"]
    U1[StoryEngineUseCase]
    U2[GenerateStoryQuestionsUseCase]
    U3[CreativeStorytellingUseCase]
    U4[VideoGenerationUseCase]
    PORTS[Ports<br/>Story / ThemedQ / Interleaved / Video / Storage]
    DTO[DTO Commands + Results]
  end

  subgraph Domain["Domain Layer (Entities + Repository Interfaces)"]
    ENT[Story / Theme / Composition / Video Models]
    REPI[Repository Interfaces]
  end

  subgraph Infra["Infrastructure Layer (Adapters)"]
    AI[Gemini + Veo Adapters]
    STORE[GCS Storage Adapter]
    DBR[Firestore Repositories]
    MEM[InMemory Repositories]
    FBA[Firebase Admin Init]
  end

  PR1 --> U1
  PR1 --> U2
  PR2 --> U3
  PR3 --> U4
  PR4 --> DBR
  SCH --> PR1
  SCH --> PR2
  SCH --> PR3

  U1 --> PORTS
  U2 --> PORTS
  U3 --> PORTS
  U4 --> PORTS
  U1 --> REPI
  U2 --> REPI
  U3 --> REPI
  U4 --> REPI
  DTO --> U1
  DTO --> U2
  DTO --> U3
  DTO --> U4
  U1 --> ENT
  U2 --> ENT
  U3 --> ENT
  U4 --> ENT

  PORTS --> AI
  PORTS --> STORE
  REPI --> DBR
  REPI --> MEM
  FBA --> DBR
```

## 3) Media Output Pipeline (Image + Video Today, Audio Planned)

```mermaid
flowchart LR
  S[Story Opening / Composition Request]
  ORCH[Use Case Orchestrator<br/>StoryEngine / CreativeStorytelling]
  TRACK[MediaTaskTracker]

  IMG[Image Generation<br/>Gemini + GCS upload]
  VID[Video Generation<br/>Veo + GCS/local storage]
  AUD[Audio Generation (Planned)<br/>TTS/Audio model + storage]

  META[Firestore Scene/Story Metadata<br/>imageUrl/videoUrl/audioUrl]
  FE[Frontend Poll/Fetch<br/>/story/media + composition endpoints]

  S --> ORCH
  ORCH --> TRACK

  ORCH --> IMG
  ORCH --> VID
  ORCH -. planned .-> AUD

  IMG --> META
  VID --> META
  AUD -. planned .-> META

  META --> FE
```

## Notes

- Current code already supports:
  - Story generation and branching metadata
  - Question generation with generated option images
  - Video job generation (`/v1/videos`)
  - Interleaved composition with `audio` and `video` part types represented in domain models (audio currently queued/placeholder in generator path)
- Current persistence mix:
  - Firestore for story/theme/user data (when configured)
  - In-memory repositories as fallback or for creative/video store in current implementation
  - Local filesystem output for video jobs under `generated_videos/`
