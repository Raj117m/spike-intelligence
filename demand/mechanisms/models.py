"""
Universal demand mechanisms.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Mechanism:

    name: str

    trigger: str

    human_change: str

    market_effect: str

    confidence: float = 0.0

    observations: int = 0
