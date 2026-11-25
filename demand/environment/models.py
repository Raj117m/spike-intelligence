from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class EnvironmentalObservation:

    source: str

    source_record_id: str

    observation_type: str

    entity: str

    location: str

    latitude: float | None

    longitude: float | None

    value: str

    numeric_value: float | None

    unit: str

    confidence: float

    observed_at: datetime

    raw_payload: str
