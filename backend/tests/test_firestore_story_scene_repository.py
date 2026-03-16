from __future__ import annotations

from app.infrastructure.repositories.firestore_story_scene_repository import FirestoreStorySceneRepository


class _FakeDocument:
    def __init__(self, doc_id: str, payload: dict) -> None:
        self.id = doc_id
        self._payload = payload

    def to_dict(self) -> dict:
        return self._payload


class _FakeSceneCollection:
    def __init__(self, docs: list[_FakeDocument]) -> None:
        self._docs = docs

    def stream(self) -> list[_FakeDocument]:
        return self._docs


class _FakeStoryDocument:
    def __init__(self, scenes: _FakeSceneCollection) -> None:
        self._scenes = scenes

    def collection(self, _name: str) -> _FakeSceneCollection:
        return self._scenes


class _FakeStoriesCollection:
    def __init__(self, story_doc: _FakeStoryDocument) -> None:
        self._story_doc = story_doc

    def document(self, _story_id: str) -> _FakeStoryDocument:
        return self._story_doc


class _FakeClient:
    def __init__(self, stories_collection: _FakeStoriesCollection) -> None:
        self._stories_collection = stories_collection

    def collection(self, _name: str) -> _FakeStoriesCollection:
        return self._stories_collection


def test_firestore_story_scene_repository_maps_scene_payload() -> None:
    repo = FirestoreStorySceneRepository(
        firestore_client=_FakeClient(
            _FakeStoriesCollection(
                _FakeStoryDocument(
                    _FakeSceneCollection(
                        [
                            _FakeDocument(
                                "scene_001",
                                {
                                    "storyId": "story_123",
                                    "chapterNumber": 1,
                                    "sceneNumber": 1,
                                    "title": "Crimson Echoes",
                                    "description": "The neon-soaked city pulses beneath you.",
                                    "shortSummary": "Kira overlooks the city.",
                                    "fullNarrative": "Long-form narrative text.",
                                    "pathDepth": 0,
                                    "isRoot": True,
                                    "isCurrentCheckpoint": True,
                                    "isEnding": False,
                                    "sceneType": "opening",
                                    "mood": "dark",
                                    "location": {
                                        "name": "Skyline Rooftop",
                                        "type": "city_rooftop",
                                    },
                                    "charactersPresent": ["kira_voss"],
                                    "assetRefs": {
                                        "heroImageId": "asset_hero_001",
                                        "sceneImageId": "asset_scene_001",
                                        "sceneVideoId": "asset_video_001",
                                        "sceneAudioId": None,
                                    },
                                    "generationStatus": {
                                        "text": "completed",
                                        "image": "completed",
                                        "video": "pending",
                                    },
                                },
                            )
                        ]
                    )
                )
            )
        ),
        stories_collection="stories",
        scenes_subcollection="scenes",
    )

    result = repo.list_by_story_id("story_123")

    assert len(result) == 1
    assert result[0].scene_id == "scene_001"
    assert result[0].story_id == "story_123"
    assert result[0].title == "Crimson Echoes"
    assert result[0].location is not None
    assert result[0].location.name == "Skyline Rooftop"
    assert result[0].asset_refs.scene_video_id == "asset_video_001"
