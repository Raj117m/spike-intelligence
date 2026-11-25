"""
Hypothesis validation.
"""

from __future__ import annotations

from .hypothesis import Hypothesis
from .models import Mechanism


def validate(
    hypothesis: Hypothesis,
    confidence: float,
    observations: int,
) -> Mechanism | None:
    """
    Promote a hypothesis to a validated mechanism if it has
    sufficient evidence.
    """

    if confidence < 0.75:
        return None

    if observations < 10:
        return None

    return Mechanism(
        name=f"{hypothesis.trigger} → {hypothesis.concept}",
        trigger=hypothesis.trigger,
        human_change=hypothesis.reason,
        market_effect=hypothesis.concept,
        confidence=confidence,
        observations=observations,
    )
