from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExportResult:
    export_id: str
    composition_id: str
    export_format: str
    download_url: str
    expires_at: datetime

