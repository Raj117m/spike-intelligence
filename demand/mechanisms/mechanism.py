"""
Scientific Mechanism Representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Mechanism:

    id: str

    name: str

    description: str

    trigger: str

    latent_state: str

    capability: str

    outcome: str

    confidence: float = 0.0

    evidence: list[str] = field(default_factory=list)

    supporting_datasets: list[str] = field(default_factory=list)

    experiments: list[str] = field(default_factory=list)

    validated: bool = False
