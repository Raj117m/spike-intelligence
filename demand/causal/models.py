"""
Core data structures for causal intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CausalEdge:
    """
    One learned causal relationship.
    """

    factor: str
    concept: str

    confidence: float

    average_lag_days: float

    evidence_count: int

    average_effect: float


@dataclass(slots=True)
class PredictionEvidence:
    """
    One observation used to update a causal edge.
    """

    factor: str

    concept: str

    observed_effect: float

    lag_days: int

    prediction_correct: bool
