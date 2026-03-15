from __future__ import annotations

from typing import Protocol

from app.domain.models.composition import Project


class ProjectRepository(Protocol):
    def create(self, project: Project) -> None:
        ...

    def get(self, project_id: str) -> Project | None:
        ...

    def save(self, project: Project) -> None:
        ...

    def list_all(self) -> list[Project]:
        ...

