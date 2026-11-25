"""
Wikipedia environmental adapter.

Adapts the existing Wikipedia ingestion pipeline into the common
EnvironmentalSource interface.
"""

from __future__ import annotations

from datetime import datetime

from demand.ingest.wikipedia import WikipediaSource

from .base import EnvironmentalSource
from .models import EnvironmentalSignal


class WikipediaEnvironmentalSource(EnvironmentalSource):

    def __init__(self, articles: list[str] | None = None, days: int = 180):
        self._source = WikipediaSource(
            articles=articles,
            days=days,
        )

    def name(self) -> str:
        return "Wikipedia"

    def fetch(self) -> list[EnvironmentalSignal]:

        data = self._source.fetch()

        observations = data["observations"]

        signals: list[EnvironmentalSignal] = []

        for _, row in observations.iterrows():

            signals.append(
                EnvironmentalSignal(
                    timestamp=datetime.combine(
                        row["ts"],
                        datetime.min.time(),
                    ),
                    source="Wikipedia",
                    topic=row["product_id"],
                    metric="pageviews",
                    value=float(row["value"]),
                    confidence=1.0,
                    metadata={},
                )
            )

        return signals
