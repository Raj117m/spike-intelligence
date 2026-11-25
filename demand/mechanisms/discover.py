"""
Mechanism Discovery Engine.

This module converts many historical observations into reusable
demand mechanisms.

This is the intellectual core of the project.
"""

from __future__ import annotations

from collections import defaultdict

from .models import Mechanism


def discover_mechanisms(
    validated_mechanisms: list[Mechanism],
    minimum_observations: int = 10,
) -> list[Mechanism]:
    """
    Merge similar validated mechanisms into universal mechanisms.
    """

    groups = defaultdict(list)

    for mechanism in validated_mechanisms:
        key = mechanism.trigger.lower()

        groups[key].append(mechanism)

    result = []

    for trigger, items in groups.items():

        observations = sum(m.observations for m in items)

        if observations < minimum_observations:
            continue

        confidence = (
            sum(
                m.confidence * m.observations
                for m in items
            )
            / observations
        )

        result.append(
            Mechanism(
                name=trigger.title(),
                trigger=trigger.title(),
                human_change="Automatically discovered",
                market_effect="Multiple concepts",
                confidence=confidence,
                observations=observations,
            )
        )

    result.sort(
        key=lambda m: (
            m.confidence,
            m.observations,
        ),
        reverse=True,
    )

    return result
