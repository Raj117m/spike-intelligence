"""
Canonical Entity Definition.

Everything in the system eventually connects to one canonical entity.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CanonicalEntity:

    asin: str

    title: str

    brand: str | None

    product_name: str

    category: str

    canonical_name: str

    wikidata_id: str | None = None

    wikipedia_title: str | None = None

    manufacturer: str | None = None

    capabilities: list[str] = field(default_factory=list)

    search_queries: list[str] = field(default_factory=list)

    aliases: list[str] = field(default_factory=list)

    confidence: float = 0.0
