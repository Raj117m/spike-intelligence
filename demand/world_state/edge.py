from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorldEdge:

    source: str

    target: str

    relation: str

    weight: float = 1.0
