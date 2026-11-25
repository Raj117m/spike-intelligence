"""
Demand Intelligence Engine.

Coordinates discovery, reasoning and causal learning.
"""

from __future__ import annotations

from demand.discovery.discover import discover
from demand.reasoning.graph import expand


class DemandIntelligenceEngine:
    """
    High-level orchestrator.

    Later this class will coordinate every subsystem in the project.
    """

    def candidate_concepts(
        self,
        product: str,
        related_topics: list[str],
    ) -> dict:

        factors = discover(product, related_topics)

        concepts = expand(set(factors))

        return {
            "product": product,
            "candidate_factors": factors,
            "expanded_concepts": sorted(concepts),
        }
