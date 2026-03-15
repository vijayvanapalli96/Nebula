from __future__ import annotations

from app.infrastructure.repositories.firestore_story_theme_repository import FirestoreStoryThemeRepository


class _FakeDocument:
    def __init__(self, doc_id: str, payload: dict) -> None:
        self.id = doc_id
        self._payload = payload

    def to_dict(self) -> dict:
        return self._payload


class _FakeCollection:
    def __init__(self, documents: list[_FakeDocument]) -> None:
        self._documents = documents

    def stream(self) -> list[_FakeDocument]:
        return self._documents


class _FakeClient:
    def __init__(self, collection: _FakeCollection) -> None:
        self._collection = collection

    def collection(self, _name: str) -> _FakeCollection:
        return self._collection


def test_list_active_maps_firestore_theme_schema_and_filters_inactive() -> None:
    repo = FirestoreStoryThemeRepository(
        firestore_client=_FakeClient(
            _FakeCollection(
                [
                    _FakeDocument(
                        "noir-detective",
                        {
                            "themeId": "noir-detective",
                            "title": "Noir Detective",
                            "description": "A rain-soaked city of secrets.",
                            "category": "mystery",
                            "heroImageUrl": "https://example.com/noir.jpg",
                            "active": True,
                            "popularityScore": 70,
                        },
                    ),
                    _FakeDocument(
                        "inactive-theme",
                        {
                            "themeId": "inactive-theme",
                            "title": "Inactive Theme",
                            "description": "Should not be returned.",
                            "category": "fantasy",
                            "heroImageUrl": "https://example.com/inactive.jpg",
                            "active": False,
                            "popularityScore": 10,
                        },
                    ),
                ]
            )
        ),
        collection_name="themes",
    )

    result = repo.list_active()

    assert len(result) == 1
    assert result[0].theme_id == "noir-detective"
    assert result[0].title == "Noir Detective"
    assert result[0].tagline == "mystery"
    assert result[0].image == "https://example.com/noir.jpg"
    assert result[0].accent_color
