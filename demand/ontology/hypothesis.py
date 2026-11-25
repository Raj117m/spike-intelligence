"""
Hypothesis Engine

Turns observations into candidate relationships that can later
be validated and added to the ontology.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Hypothesis:
    source: str
    relationship: str
    target: str
    evidence: str
    confidence: float


def create_hypothesis(
    source: str,
    relationship: str,
    target: str,
    evidence: str,
    confidence: float = 0.5,
) -> Hypothesis:

    return Hypothesis(
        source=source,
        relationship=relationship,
        target=target,
        evidence=evidence,
        confidence=confidence,
    )
