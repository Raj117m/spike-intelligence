"""
Environmental source registry.

Coordinates all environmental data sources.
"""

from __future__ import annotations

from .base import EnvironmentalSource
from .models import EnvironmentalSignal


class EnvironmentalRegistry:

    def __init__(self) -> None:
        self._sources: list[EnvironmentalSource] = []

    def register(
        self,
        source: EnvironmentalSource,
    ) -> None:
        self._sources.append(source)

    def sources(self) -> list[str]:
        return [s.name() for s in self._sources]

    def fetch_all(self) -> list[EnvironmentalSignal]:

        signals: list[EnvironmentalSignal] = []

        for source in self._sources:
            signals.extend(source.fetch())

        return signals
