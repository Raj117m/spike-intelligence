from dataclasses import dataclass

from demand.environment.models import EnvironmentalObservation


@dataclass(slots=True)
class ActivatedFactor:

    factor: str

    strength: float

    reason: str


class FactorEngine:

    def analyze(
        self,
        observation: EnvironmentalObservation,
    ):

        factors = []

        t = observation.observation_type.lower()

        if "rain" in t:

            factors.append(
                ActivatedFactor(
                    "HEAVY_RAIN",
                    observation.confidence,
                    "Rainfall observation",
                )
            )

        if "aqi" in t:

            factors.append(
                ActivatedFactor(
                    "AIR_POLLUTION",
                    observation.confidence,
                    "AQI observation",
                )
            )

        if "price" in t:

            factors.append(
                ActivatedFactor(
                    "PRICE_MOVEMENT",
                    observation.confidence,
                    "Market observation",
                )
            )

        if "power" in t:

            factors.append(
                ActivatedFactor(
                    "POWER_DISRUPTION",
                    observation.confidence,
                    "Power observation",
                )
            )

        return factors
