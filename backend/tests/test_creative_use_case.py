from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.application.dto.creative_commands import (
    CreateAssetUploadCommand,
    CreateCompositionCommand,
    CreateProjectCommand,
    RegenerateCompositionPartCommand,
)
from app.application.ports.interleaved_generator import (
    InterleavedGenerationRequest,
    InterleavedGenerationResult,
)
from app.application.use_cases.creative_storytelling import CreativeStorytellingUseCase
from app.domain.models.composition import CompositionPart, GenerationUsage
from app.infrastructure.repositories.in_memory_creative_repository import (
    InMemoryAssetRepository,
    InMemoryCompositionRepository,
    InMemoryCreativeWorkspaceRepository,
    InMemoryProjectRepository,
    InMemoryUsageRepository,
)


class FakeInterleavedGenerator:
    async def generate(self, request: InterleavedGenerationRequest) -> InterleavedGenerationResult:
        now = datetime.now(UTC)
        parts = [
            CompositionPart(
                part_id="part-1",
                type="text",
                sequence=1,
                status="completed",
                content="Narration chunk",
                created_at=now,
                updated_at=now,
            ),
            CompositionPart(
                part_id="part-2",
                type="image",
                sequence=2,
                status="completed",
                asset_uri="https://cdn.example.com/shot.png",
                mime_type="image/png",
                created_at=now,
                updated_at=now,
            ),
        ]
        return InterleavedGenerationResult(
            parts=parts,
            usage=GenerationUsage(prompt_tokens=20, output_tokens=80, image_count=1),
        )

    async def regenerate_part(
        self,
        request: InterleavedGenerationRequest,
        original_part: CompositionPart,
        instruction: str | None = None,
    ) -> CompositionPart:
        now = datetime.now(UTC)
        return CompositionPart(
            part_id=original_part.part_id,
            type=original_part.type,
            sequence=original_part.sequence,
            status="completed",
            content=instruction or "Regenerated content",
            created_at=original_part.created_at,
            updated_at=now,
        )


def _build_use_case() -> CreativeStorytellingUseCase:
    workspace = InMemoryCreativeWorkspaceRepository()
    return CreativeStorytellingUseCase(
        project_repository=InMemoryProjectRepository(workspace),
        composition_repository=InMemoryCompositionRepository(workspace),
        asset_repository=InMemoryAssetRepository(workspace),
        usage_repository=InMemoryUsageRepository(workspace),
        generator=FakeInterleavedGenerator(),
    )


def test_create_composition_and_usage_update() -> None:
    use_case = _build_use_case()
    project = use_case.create_project(
        CreateProjectCommand(
            title="Storybook",
            use_case="interactive_storybook",
            tone="whimsical",
            style_bible={"palette": "pastel"},
        )
    )

    composition = asyncio.run(
        use_case.create_composition(
            CreateCompositionCommand(
                prompt="A fox explores a moonlit forest.",
                target_platform="web",
                project_id=project.project_id,
                requested_modalities=["text", "image"],
            )
        )
    )

    assert composition.status == "completed"
    assert len(composition.parts) == 2
    assert use_case.get_usage().image_count == 1


def test_regenerate_part_and_asset_upload_flow() -> None:
    use_case = _build_use_case()
    composition = asyncio.run(
        use_case.create_composition(
            CreateCompositionCommand(
                prompt="Explain gravity simply.",
                target_platform="social",
                requested_modalities=["text"],
            )
        )
    )

    updated = asyncio.run(
        use_case.regenerate_part(
            RegenerateCompositionPartCommand(
                composition_id=composition.composition_id,
                part_id=composition.parts[0].part_id,
                instruction="Make it more playful.",
            )
        )
    )
    assert updated.version == 2
    assert updated.parts[0].content == "Make it more playful."

    asset = use_case.create_asset_upload(
        CreateAssetUploadCommand(filename="poster.png", mime_type="image/png")
    )
    assert asset.upload_url.startswith("https://")
    assert use_case.get_asset(asset.asset_id).filename == "poster.png"

