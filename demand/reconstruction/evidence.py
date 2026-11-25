"""
Historical Evidence Package.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EvidencePackage:

    asin: str

    title: str

    category: str

    velocity: float

    wikipedia_topic: str | None = None

    news_query: str | None = None

    weather_region: str | None = None

    economic_region: str | None = None

    notes: str = ""
