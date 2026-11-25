"""
Persistent causal graph.
"""

from __future__ import annotations

from collections import defaultdict

from demand.discovery.evidence import Evidence

from .models import CausalEdge


class CausalGraph:
    """
    Stores learned causal relationships together with evidence.
    """

    def __init__(self):
        self._edges: dict[str, dict[str, CausalEdge]] = defaultdict(dict)
        self._evidence: dict[str, dict[str, Evidence]] = defaultdict(dict)

    def add(self, edge: CausalEdge) -> None:
        self._edges[edge.factor][edge.concept] = edge
        self._evidence[edge.factor][edge.concept] = Evidence()

    def edge(self, factor: str, concept: str) -> CausalEdge | None:
        return self._edges.get(factor, {}).get(concept)

    def evidence(self, factor: str, concept: str) -> Evidence | None:
        return self._evidence.get(factor, {}).get(concept)

    def concepts(self, factor: str) -> list[CausalEdge]:
        return list(self._edges.get(factor, {}).values())

    def factors(self) -> list[str]:
        return sorted(self._edges)
