from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Observation:

    source: str

    observation_type: str

    entity: str

    location: str

    value: float | str

    unit: str

    observed_at: datetime

    confidence: float

    raw_source: str
