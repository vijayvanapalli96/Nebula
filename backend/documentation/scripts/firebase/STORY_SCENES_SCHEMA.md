# Firestore Story Scenes Schema

Path:
- `/stories/{storyId}/scenes/{sceneId}`

Configurable via environment:
- `FIREBASE_STORIES_COLLECTION` (default: `stories`)
- `FIREBASE_SCENES_SUBCOLLECTION` (default: `scenes`)

Required fields per scene document:
- `sceneId` (string)
- `storyId` (string)
- `chapterNumber` (number)
- `sceneNumber` (number)
- `title` (string)
- `description` (string)

Recommended fields for frontend graph + scene playback:
- `shortSummary` (string)
- `fullNarrative` (string)
- `parentSceneId` (string | null)
- `selectedChoiceIdFromParent` (string | null)
- `pathDepth` (number)
- `isRoot` (boolean)
- `isCurrentCheckpoint` (boolean)
- `isEnding` (boolean)
- `endingType` (string | null)
- `sceneType` (`opening|exploration|dialogue|action|twist|climax|ending`)
- `mood` (string)
- `location` (map)
- `charactersPresent` (array<string>)
- `assetRefs` (map)
- `generationStatus` (map)
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

Example document:

```json
{
  "sceneId": "scene_001",
  "storyId": "story_123",
  "chapterNumber": 1,
  "sceneNumber": 1,
  "title": "Crimson Echoes",
  "description": "The neon-soaked city pulses beneath you...",
  "shortSummary": "Kira overlooks the city and spots three possible paths.",
  "fullNarrative": "Long form narrative goes here.",
  "parentSceneId": null,
  "selectedChoiceIdFromParent": null,
  "pathDepth": 0,
  "isRoot": true,
  "isCurrentCheckpoint": true,
  "isEnding": false,
  "endingType": null,
  "sceneType": "opening",
  "mood": "dark",
  "location": {
    "name": "Skyline Rooftop",
    "type": "city_rooftop"
  },
  "charactersPresent": ["kira_voss"],
  "assetRefs": {
    "heroImageId": "asset_hero_001",
    "sceneImageId": "asset_scene_001",
    "sceneVideoId": "asset_video_001",
    "sceneAudioId": null
  },
  "generationStatus": {
    "text": "completed",
    "image": "completed",
    "video": "completed"
  },
  "createdAt": "server timestamp",
  "updatedAt": "server timestamp"
}
```

Endpoint powered by this schema:
- `GET /stories/{storyId}/scenes`
