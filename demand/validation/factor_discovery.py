from dataclasses import dataclass


@dataclass(slots=True)
class CandidateFactor:

    name: str

    reason: str

    confidence: float


class FactorDiscovery:

    def discover(

        self,

        mechanism,

        observations,

        prediction_correct,

    ):

        if prediction_correct:

            return []

        discovered = []

        for obs in observations:

            discovered.append(

                CandidateFactor(

                    name=f"{obs.observation_type.upper()}_INFLUENCE",

                    reason=f"Observed {obs.observation_type} during failed prediction.",

                    confidence=0.20,

                )

            )

        return discovered
