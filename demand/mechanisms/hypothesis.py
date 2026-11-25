"""
Hypothesis generation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Hypothesis:

    trigger: str

    concept: str

    reason: str

    confidence: float = 0.0


def propose(
    trigger: str,
    concepts: list[str],
) -> list[Hypothesis]:

    return [
        Hypothesis(
            trigger=trigger,
            concept=concept,
            reason="Automatically generated candidate",
        )
        for concept in concepts
    ]
