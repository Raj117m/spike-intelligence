"""
Feature model.

A Feature is the normalized representation of an environmental signal.
"""

from __future__ import annotations

from dataclasses import dataclass

from demand.environment.models import EnvironmentalSignal


@dataclass(slots=True)
class Feature:

    topic: str

    source: str

    name: str

    value: float

    signal: EnvironmentalSignal
