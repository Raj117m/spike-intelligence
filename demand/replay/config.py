from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class ReplayConfig:

    replay_start: date

    replay_end: date

    window_days: int = 60

    step_days: int = 1

    min_signature_support: int = 3

    prediction_threshold: float = 0.60

    auto_promote: bool = True

    auto_demote: bool = True

    save_every: int = 10
