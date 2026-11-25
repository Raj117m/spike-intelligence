"""
Unified environmental state.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import EnvironmentalSignal


@dataclass(slots=True)
class EnvironmentalState:

    topic: str

    signals: list[EnvironmentalSignal]

    score: float

    confidence: float
