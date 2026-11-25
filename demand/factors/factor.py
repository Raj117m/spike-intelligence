"""
Environmental Factor Definition.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class EnvironmentalFactor:

    id: str

    name: str

    category: str

    unit: str

    geography: str

    source: str

    source_url: str

    update_frequency: str

    current_value: float | None

    observed_at: datetime | None

    confidence: float

    discovery_method: str

    active: bool = True
