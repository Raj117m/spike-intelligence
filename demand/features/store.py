"""
Feature Store.

Central storage for normalized environmental features.
"""

from __future__ import annotations

from collections import defaultdict

from .models import Feature


class FeatureStore:

    def __init__(self) -> None:
        self._features: dict[str, list[Feature]] = defaultdict(list)

    def add(self, feature: Feature) -> None:
        self._features[feature.topic].append(feature)

    def add_many(self, features: list[Feature]) -> None:
        for feature in features:
            self.add(feature)

    def topics(self) -> list[str]:
        return sorted(self._features.keys())

    def features(self, topic: str) -> list[Feature]:
        return list(self._features.get(topic, []))

    def all(self) -> dict[str, list[Feature]]:
        return dict(self._features)

    def clear(self) -> None:
        self._features.clear()
