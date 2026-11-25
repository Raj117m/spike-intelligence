"""
Signal fusion.
"""

from __future__ import annotations

from collections import defaultdict

from .models import EnvironmentalSignal
from .state import EnvironmentalState


def fuse(
    signals: list[EnvironmentalSignal],
) -> list[EnvironmentalState]:

    groups = defaultdict(list)

    for signal in signals:
        groups[signal.topic].append(signal)

    states = []

    for topic, items in groups.items():

        score = sum(s.value for s in items) / len(items)

        confidence = (
            sum(s.confidence for s in items)
            / len(items)
        )

        states.append(
            EnvironmentalState(
                topic=topic,
                signals=items,
                score=score,
                confidence=confidence,
            )
        )

    return sorted(
        states,
        key=lambda s: s.score,
        reverse=True,
    )
