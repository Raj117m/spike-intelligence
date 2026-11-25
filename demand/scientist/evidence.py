from dataclasses import dataclass


@dataclass(slots=True)
class Evidence:

    experiment: str

    variable: str

    effect_size: float

    p_value: float

    supported: bool
