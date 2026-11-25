"""
Historical validation experiment.

Runs the complete prediction pipeline on historical events and
reports evaluation metrics.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HistoricalExperiment:

    name: str

    start_date: str

    end_date: str

    description: str


BLACK_FRIDAY_2023 = HistoricalExperiment(
    name="Black Friday 2023",
    start_date="2023-11-20",
    end_date="2023-11-30",
    description="Large retail promotion",
)


def experiments() -> list[HistoricalExperiment]:
    return [
        BLACK_FRIDAY_2023,
    ]
