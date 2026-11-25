from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Evidence:

    mechanism_id: str

    source: str

    dataset: str

    entity: str

    observation: str

    observed_at: datetime

    confidence: float

    url: str | None = None
