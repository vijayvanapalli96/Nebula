from __future__ import annotations

from datetime import UTC, datetime

from app.infrastructure.repositories.firestore_user_story_repository import FirestoreUserStoryRepository


class _FakeDocument:
    def __init__(self, doc_id: str, payload: dict) -> None:
        self.id = doc_id
        self._payload = payload

    def to_dict(self) -> dict:
        return self._payload


class _FakeStoriesCollection:
    def __init__(self, docs: list[_FakeDocument]) -> None:
        self._docs = docs

    def stream(self) -> list[_FakeDocument]:
        return self._docs


class _FakeUserDocument:
    def __init__(self, stories: _FakeStoriesCollection) -> None:
        self._stories = stories

    def collection(self, _name: str) -> _FakeStoriesCollection:
        return self._stories


class _FakeUsersCollection:
    def __init__(self, user_doc: _FakeUserDocument) -> None:
        self._user_doc = user_doc

    def document(self, _user_id: str) -> _FakeUserDocument:
        return self._user_doc


class _FakeClient:
    def __init__(self, users_collection: _FakeUsersCollection) -> None:
        self._users_collection = users_collection

    def collection(self, _name: str) -> _FakeUsersCollection:
        return self._users_collection


def test_firestore_user_story_repository_maps_user_story_docs() -> None:
    repo = FirestoreUserStoryRepository(
        firestore_client=_FakeClient(
            _FakeUsersCollection(
                _FakeUserDocument(
                    _FakeStoriesCollection(
                        [
                            _FakeDocument(
                                "story_a",
                                {
                                    "storyId": "story_a",
                                    "title": "Crimson Echoes",
                                    "genre": "Noir",
                                    "characterName": "Kira Voss",
                                    "archetype": "Detective",
                                    "lastSceneId": "scene_003",
                                    "choicesAvailable": 3,
                                    "progress": 55,
                                    "coverImage": "https://example.com/story-a.jpg",
                                    "updatedAt": datetime(2026, 3, 12, 10, 0, tzinfo=UTC),
                                },
                            ),
                            _FakeDocument(
                                "story_b",
                                {
                                    "storyId": "story_b",
                                    "themeTitle": "Silicon Ashes",
                                    "themeCategory": "Sci-Fi",
                                    "status": "questions_generated",
                                    "questionCount": 4,
                                    "updatedAt": datetime(2026, 3, 14, 10, 0, tzinfo=UTC),
                                },
                            ),
                        ]
                    )
                )
            )
        ),
        users_collection="users",
        stories_subcollection="stories",
    )

    result = repo.list_by_user_id("tmduUAxT4nNHLQDWmKsb9bf58342")

    assert len(result) == 2
    assert result[0].story_id == "story_b"
    assert result[0].genre == "Sci-Fi"
    assert result[0].title == "Silicon Ashes"
    assert result[0].status == "questions_generated"
    assert result[0].choices_available == 4
    assert result[1].story_id == "story_a"
    assert result[1].choices_available == 3
    assert result[1].progress == 55
