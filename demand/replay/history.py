"""
Historical Replay Engine.

Replays historical observations in chronological order so every
hypothesis is evaluated exactly as it would have appeared in real time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Observation:
    timestamp: datetime
    source: str
    topic: str
    value: float


class ReplayEngine:

    def __init__(self, observations: list[Observation]) -> None:
        self._observations = sorted(
            observations,
            key=lambda x: x.timestamp,
        )

    def replay(self):
        for obs in self._observations:
            yield obs

    def between(
        self,
        start: datetime,
        end: datetime,
    ):
        for obs in self._observations:
            if start <= obs.timestamp <= end:
                yield obs
