from dataclasses import dataclass

from demand.environment.factor_engine import ActivatedFactor


@dataclass(slots=True)
class ActivatedMechanism:

    mechanism: str

    confidence: float

    factors: list[str]


class MechanismEngine:

    def infer(self, factors):

        names = {f.factor for f in factors}

        mechanisms = []

        if "HEAVY_RAIN" in names:

            mechanisms.append(

                ActivatedMechanism(

                    mechanism="FLOOD_SUPPLY_CHAIN",

                    confidence=0.85,

                    factors=list(names),

                )

            )

        if "AIR_POLLUTION" in names:

            mechanisms.append(

                ActivatedMechanism(

                    mechanism="HEALTH_PROTECTION",

                    confidence=0.90,

                    factors=list(names),

                )

            )

        if "PRICE_MOVEMENT" in names:

            mechanisms.append(

                ActivatedMechanism(

                    mechanism="MARKET_REPRICING",

                    confidence=0.80,

                    factors=list(names),

                )

            )

        return mechanisms
