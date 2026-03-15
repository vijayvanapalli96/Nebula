from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock

from app.domain.models.composition import AssetRecord, Composition, GenerationUsage, Project
from app.domain.repositories.asset_repository import AssetRepository
from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.usage_repository import UsageRepository


class InMemoryCreativeWorkspaceRepository(
    ProjectRepository,
    CompositionRepository,
    AssetRepository,
    UsageRepository,
):
    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._compositions: dict[str, Composition] = {}
        self._assets: dict[str, AssetRecord] = {}
        self._usage = GenerationUsage()
        self._lock = RLock()

    # ProjectRepository
    def create(self, item: Project | Composition | AssetRecord) -> None:  # type: ignore[override]
        with self._lock:
            if isinstance(item, Project):
                item.updated_at = datetime.now(UTC)
                self._projects[item.project_id] = deepcopy(item)
                return
            if isinstance(item, Composition):
                item.updated_at = datetime.now(UTC)
                self._compositions[item.composition_id] = deepcopy(item)
                return
            if isinstance(item, AssetRecord):
                item.updated_at = datetime.now(UTC)
                self._assets[item.asset_id] = deepcopy(item)
                return
            raise TypeError(f"Unsupported entity type: {type(item)!r}")

    def get(self, entity_id: str) -> Project | Composition | AssetRecord | None:  # type: ignore[override]
        with self._lock:
            if entity_id in self._projects:
                return deepcopy(self._projects[entity_id])
            if entity_id in self._compositions:
                return deepcopy(self._compositions[entity_id])
            if entity_id in self._assets:
                return deepcopy(self._assets[entity_id])
            return None

    def save(self, item: Project | Composition | AssetRecord) -> None:  # type: ignore[override]
        with self._lock:
            item.updated_at = datetime.now(UTC)
            if isinstance(item, Project):
                self._projects[item.project_id] = deepcopy(item)
                return
            if isinstance(item, Composition):
                self._compositions[item.composition_id] = deepcopy(item)
                return
            if isinstance(item, AssetRecord):
                self._assets[item.asset_id] = deepcopy(item)
                return
            raise TypeError(f"Unsupported entity type: {type(item)!r}")

    def list_all(self) -> list[Project | Composition | AssetRecord]:  # type: ignore[override]
        with self._lock:
            values: list[Project | Composition | AssetRecord] = []
            values.extend(deepcopy(project) for project in self._projects.values())
            values.extend(deepcopy(composition) for composition in self._compositions.values())
            values.extend(deepcopy(asset) for asset in self._assets.values())
            return values

    # UsageRepository
    def add_usage(self, usage: GenerationUsage) -> None:
        with self._lock:
            self._usage.merge(usage)

    def get_usage(self) -> GenerationUsage:
        with self._lock:
            return deepcopy(self._usage)

    # Typed helper methods for DI wrappers
    def create_project(self, project: Project) -> None:
        self.create(project)

    def get_project(self, project_id: str) -> Project | None:
        project = self.get(project_id)
        return project if isinstance(project, Project) else None

    def save_project(self, project: Project) -> None:
        self.save(project)

    def list_projects(self) -> list[Project]:
        return [item for item in self.list_all() if isinstance(item, Project)]

    def create_composition(self, composition: Composition) -> None:
        self.create(composition)

    def get_composition(self, composition_id: str) -> Composition | None:
        composition = self.get(composition_id)
        return composition if isinstance(composition, Composition) else None

    def save_composition(self, composition: Composition) -> None:
        self.save(composition)

    def list_compositions(self) -> list[Composition]:
        return [item for item in self.list_all() if isinstance(item, Composition)]

    def create_asset(self, asset: AssetRecord) -> None:
        self.create(asset)

    def get_asset(self, asset_id: str) -> AssetRecord | None:
        asset = self.get(asset_id)
        return asset if isinstance(asset, AssetRecord) else None

    def save_asset(self, asset: AssetRecord) -> None:
        self.save(asset)

    def list_assets(self) -> list[AssetRecord]:
        return [item for item in self.list_all() if isinstance(item, AssetRecord)]


class InMemoryProjectRepository(ProjectRepository):
    def __init__(self, workspace: InMemoryCreativeWorkspaceRepository) -> None:
        self._workspace = workspace

    def create(self, project: Project) -> None:
        self._workspace.create_project(project)

    def get(self, project_id: str) -> Project | None:
        return self._workspace.get_project(project_id)

    def save(self, project: Project) -> None:
        self._workspace.save_project(project)

    def list_all(self) -> list[Project]:
        return self._workspace.list_projects()


class InMemoryCompositionRepository(CompositionRepository):
    def __init__(self, workspace: InMemoryCreativeWorkspaceRepository) -> None:
        self._workspace = workspace

    def create(self, composition: Composition) -> None:
        self._workspace.create_composition(composition)

    def get(self, composition_id: str) -> Composition | None:
        return self._workspace.get_composition(composition_id)

    def save(self, composition: Composition) -> None:
        self._workspace.save_composition(composition)

    def list_all(self) -> list[Composition]:
        return self._workspace.list_compositions()


class InMemoryAssetRepository(AssetRepository):
    def __init__(self, workspace: InMemoryCreativeWorkspaceRepository) -> None:
        self._workspace = workspace

    def create(self, asset: AssetRecord) -> None:
        self._workspace.create_asset(asset)

    def get(self, asset_id: str) -> AssetRecord | None:
        return self._workspace.get_asset(asset_id)

    def save(self, asset: AssetRecord) -> None:
        self._workspace.save_asset(asset)

    def list_all(self) -> list[AssetRecord]:
        return self._workspace.list_assets()


class InMemoryUsageRepository(UsageRepository):
    def __init__(self, workspace: InMemoryCreativeWorkspaceRepository) -> None:
        self._workspace = workspace

    def add_usage(self, usage: GenerationUsage) -> None:
        self._workspace.add_usage(usage)

    def get_usage(self) -> GenerationUsage:
        return self._workspace.get_usage()
