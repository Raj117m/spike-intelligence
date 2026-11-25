"""
Mechanism scoring.

Scores known mechanisms using normalized environmental features.
"""

from __future__ import annotations

from dataclasses import dataclass

from demand.features.models import Feature


@dataclass(slots=True)
class MechanismScore:

    mechanism: str

    score: float

    confidence: float

    supporting_features: list[Feature]


def score_mechanism(
    name: str,
    features: list[Feature],
) -> MechanismScore:

    if not features:
        return MechanismScore(
            mechanism=name,
            score=0.0,
            confidence=0.0,
            supporting_features=[],
        )

    score = sum(f.value for f in features) / len(features)

    confidence = min(
        1.0,
        len(features) / 10.0,
    )

    return MechanismScore(
        mechanism=name,
        score=score,
        confidence=confidence,
        supporting_features=features,
    )
