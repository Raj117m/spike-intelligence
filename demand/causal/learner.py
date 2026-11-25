"""
Learns from prediction outcomes by updating evidence.
"""

from __future__ import annotations

from .graph import CausalGraph
from .models import PredictionEvidence


def update(
    graph: CausalGraph,
    evidence: PredictionEvidence,
) -> None:

    edge = graph.edge(
        evidence.factor,
        evidence.concept,
    )

    if edge is None:
        return

    ev = graph.evidence(
        evidence.factor,
        evidence.concept,
    )

    if ev is None:
        return

    ev.record(
        effect=evidence.observed_effect,
        lag=evidence.lag_days,
        success=evidence.prediction_correct,
    )

    edge.evidence_count = ev.observations
    edge.average_effect = ev.average_effect
    edge.average_lag_days = ev.average_lag
    edge.confidence = ev.confidence
