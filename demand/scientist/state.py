"""
Market State Estimation.
"""

from __future__ import annotations

from dataclasses import dataclass

from demand.scientist.variable import LatentVariable


@dataclass(slots=True)
class MarketState:

    variables: list[LatentVariable]

    @property
    def confidence(self) -> float:

        if not self.variables:
            return 0.0

        return sum(v.confidence for v in self.variables) / len(self.variables)


class StateEstimator:

    def estimate(self, variables: list[LatentVariable]) -> MarketState:

        return MarketState(variables)
