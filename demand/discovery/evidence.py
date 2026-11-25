"""
Evidence accumulation for causal relationships.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Evidence:

    observations: int = 0

    successful_predictions: int = 0

    failed_predictions: int = 0

    cumulative_effect: float = 0.0

    cumulative_lag: float = 0.0

    def record(
        self,
        *,
        effect: float,
        lag: float,
        success: bool,
    ) -> None:

        self.observations += 1

        self.cumulative_effect += effect

        self.cumulative_lag += lag

        if success:
            self.successful_predictions += 1
        else:
            self.failed_predictions += 1

    @property
    def average_effect(self) -> float:

        if self.observations == 0:
            return 0.0

        return self.cumulative_effect / self.observations

    @property
    def average_lag(self) -> float:

        if self.observations == 0:
            return 0.0

        return self.cumulative_lag / self.observations

    @property
    def confidence(self) -> float:

        total = self.successful_predictions + self.failed_predictions

        if total == 0:
            return 0.0

        return self.successful_predictions / total
