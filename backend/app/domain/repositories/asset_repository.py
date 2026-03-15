from __future__ import annotations

from typing import Protocol

from app.domain.models.composition import AssetRecord


class AssetRepository(Protocol):
    def create(self, asset: AssetRecord) -> None:
        ...

    def get(self, asset_id: str) -> AssetRecord | None:
        ...

    def save(self, asset: AssetRecord) -> None:
        ...

    def list_all(self) -> list[AssetRecord]:
        ...

