"""
Snapshot Engine.

Captures the system's view of the world at a specific point in time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .history import Observation


@dataclass(slots=True)
class Snapshot:
    timestamp: datetime
    observations: list[Observation]


def build_snapshot(
    observations: list[Observation],
    timestamp: datetime,
) -> Snapshot:

    visible = [
        o
        for o in observations
        if o.timestamp <= timestamp
    ]

    return Snapshot(
        timestamp=timestamp,
        observations=visible,
    )
