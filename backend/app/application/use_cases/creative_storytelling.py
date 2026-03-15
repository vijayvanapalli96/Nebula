from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.application.dto.creative_commands import (
    CreateAssetUploadCommand,
    CreateCompositionCommand,
    CreateProjectCommand,
    ExportCompositionCommand,
    RegenerateCompositionPartCommand,
)
from app.application.dto.creative_results import ExportResult
from app.application.errors import (
    AssetNotFoundError,
    CompositionNotFoundError,
    PartNotFoundError,
    ProjectNotFoundError,
)
from app.application.ports.interleaved_generator import (
    InterleavedGenerationRequest,
    InterleavedGeneratorPort,
)
from app.domain.models.composition import (
    AssetRecord,
    Composition,
    CompositionPart,
    GenerationUsage,
    Project,
)
from app.domain.repositories.asset_repository import AssetRepository
from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.usage_repository import UsageRepository


class CreativeStorytellingUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        composition_repository: CompositionRepository,
        asset_repository: AssetRepository,
        usage_repository: UsageRepository,
        generator: InterleavedGeneratorPort,
    ) -> None:
        self._project_repository = project_repository
        self._composition_repository = composition_repository
        self._asset_repository = asset_repository
        self._usage_repository = usage_repository
        self._generator = generator

    def create_project(self, command: CreateProjectCommand) -> Project:
        project = Project(
            project_id=str(uuid4()),
            title=command.title.strip(),
            use_case=command.use_case.strip(),
            tone=command.tone.strip() if command.tone else None,
            style_bible=command.style_bible,
        )
        self._project_repository.create(project)
        return project

    async def create_composition(self, command: CreateCompositionCommand) -> Composition:
        project = self._get_project_if_present(command.project_id)
        composition = Composition(
            composition_id=str(uuid4()),
            project_id=project.project_id if project else None,
            prompt=command.prompt.strip(),
            target_platform=command.target_platform.strip(),
            status="generating",
            requested_modalities=command.requested_modalities,
        )
        self._composition_repository.create(composition)

        generation_request = InterleavedGenerationRequest(
            prompt=command.prompt,
            requested_modalities=command.requested_modalities,
            style_bible=project.style_bible if project else {},
            max_parts=command.max_parts,
        )
        generation_result = await self._generator.generate(generation_request)
        composition.parts = generation_result.parts
        composition.usage.merge(generation_result.usage)
        composition.status = self._resolve_composition_status(generation_result.parts)
        composition.updated_at = datetime.now(UTC)
        self._composition_repository.save(composition)
        self._usage_repository.add_usage(generation_result.usage)
        return composition

    def get_composition(self, composition_id: str) -> Composition:
        composition = self._composition_repository.get(composition_id)
        if composition is None:
            raise CompositionNotFoundError(f"Composition '{composition_id}' not found.")
        return composition

    async def regenerate_part(self, command: RegenerateCompositionPartCommand) -> Composition:
        composition = self.get_composition(command.composition_id)
        part, index = self._find_part(composition.parts, command.part_id)

        project = self._get_project_if_present(composition.project_id)
        request = InterleavedGenerationRequest(
            prompt=composition.prompt,
            requested_modalities=composition.requested_modalities,
            style_bible=project.style_bible if project else {},
            max_parts=1,
        )
        regenerated_part = await self._generator.regenerate_part(
            request=request,
            original_part=part,
            instruction=command.instruction,
        )
        regenerated_part.part_id = part.part_id
        regenerated_part.sequence = part.sequence
        regenerated_part.updated_at = datetime.now(UTC)
        composition.parts[index] = regenerated_part
        composition.version += 1
        composition.updated_at = datetime.now(UTC)
        composition.status = self._resolve_composition_status(composition.parts)
        self._composition_repository.save(composition)
        return composition

    def create_asset_upload(self, command: CreateAssetUploadCommand) -> AssetRecord:
        asset_id = str(uuid4())
        normalized_name = command.filename.strip().replace(" ", "_")
        upload_url = (
            f"https://storage.googleapis.com/upload/creative-story-assets/"
            f"{asset_id}/{normalized_name}?signature=mock"
        )
        storage_uri = f"gs://creative-story-assets/{asset_id}/{normalized_name}"
        asset = AssetRecord(
            asset_id=asset_id,
            filename=normalized_name,
            mime_type=command.mime_type.strip(),
            upload_url=upload_url,
            storage_uri=storage_uri,
            expires_at=AssetRecord.expires_after(command.expires_in_minutes),
        )
        self._asset_repository.create(asset)
        return asset

    def get_asset(self, asset_id: str) -> AssetRecord:
        asset = self._asset_repository.get(asset_id)
        if asset is None:
            raise AssetNotFoundError(f"Asset '{asset_id}' not found.")
        return asset

    def export_composition(self, command: ExportCompositionCommand) -> ExportResult:
        composition = self.get_composition(command.composition_id)
        export_id = str(uuid4())
        safe_format = command.export_format.strip().lower()
        download_url = (
            "https://storage.googleapis.com/creative-story-exports/"
            f"{composition.composition_id}/{export_id}.{safe_format}?token=mock"
        )
        return ExportResult(
            export_id=export_id,
            composition_id=composition.composition_id,
            export_format=safe_format,
            download_url=download_url,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

    def get_usage(self) -> GenerationUsage:
        return self._usage_repository.get_usage()

    def build_stream_events(self, composition_id: str) -> list[dict[str, str]]:
        composition = self.get_composition(composition_id)
        events: list[dict[str, str]] = []
        events.append(
            {
                "event": "composition_status",
                "data": f"{composition.composition_id}|{composition.status}|v{composition.version}",
            }
        )
        for part in sorted(composition.parts, key=lambda item: item.sequence):
            payload = (
                f"{part.part_id}|{part.type}|{part.status}|"
                f"{part.content or part.asset_uri or ''}"
            )
            events.append({"event": "part", "data": payload})
        events.append({"event": "done", "data": composition.composition_id})
        return events

    def _get_project_if_present(self, project_id: str | None) -> Project | None:
        if not project_id:
            return None
        project = self._project_repository.get(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project '{project_id}' not found.")
        return project

    @staticmethod
    def _find_part(parts: list[CompositionPart], part_id: str) -> tuple[CompositionPart, int]:
        for index, part in enumerate(parts):
            if part.part_id == part_id:
                return part, index
        raise PartNotFoundError(f"Part '{part_id}' not found in composition.")

    @staticmethod
    def _resolve_composition_status(parts: list[CompositionPart]) -> str:
        if not parts:
            return "failed"
        statuses = {part.status for part in parts}
        if statuses == {"completed"}:
            return "completed"
        if "failed" in statuses:
            return "failed"
        if "queued" in statuses or "generating" in statuses:
            return "partial"
        return "partial"

