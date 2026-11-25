"""
Scientific definition of latent market variables.

A latent variable is NOT directly observable.
It is estimated from one or more public sensors and must earn
its place in the Market State Vector through repeated experiments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class LatentVariable:
    """
    Scientific representation of one latent market variable.
    """

    name: str
    definition: str

    proxies: List[str] = field(default_factory=list)

    sensors: List[str] = field(default_factory=list)

    confidence: float = 0.0

    evidence_count: int = 0

    experiments: List[str] = field(default_factory=list)

    validated: bool = False

    notes: str = ""


class VariableRegistry:

    def __init__(self):

        self._variables: dict[str, LatentVariable] = {}

    def register(self, variable: LatentVariable):

        self._variables[variable.name] = variable

    def get(self, name: str) -> LatentVariable:

        return self._variables[name]

    def all(self):

        return list(self._variables.values())
