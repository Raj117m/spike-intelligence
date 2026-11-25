from dataclasses import dataclass


@dataclass(slots=True)
class SensorReading:

    sensor: str

    variable: str

    value: float

    timestamp: str
