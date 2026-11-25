from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorldNode:

    id: str

    node_type: str

    name: str

    confidence: float = 1.0
