"""
Demand Intelligence execution cycle.
"""

from __future__ import annotations

from dataclasses import dataclass

from .engine import DemandIntelligenceEngine


@dataclass(slots=True)
class CycleResult:
    product: str
    factors: list[str]
    concepts: list[str]


def run_cycle(
    product: str,
    related_topics: list[str],
) -> CycleResult:

    engine = DemandIntelligenceEngine()

    result = engine.candidate_concepts(
        product,
        related_topics,
    )

    return CycleResult(
        product=result["product"],
        factors=result["candidate_factors"],
        concepts=result["expanded_concepts"],
    )
