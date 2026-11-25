from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ActivatedConstraint:

    constraint_id: str

    trigger: str

    strength: float

    source: str

    evidence: str


class ConstraintActivator:

    RULES = {

        "STORM": ("C0001", 0.95),

        "FLOOD": ("C0004", 0.90),

        "EARTHQUAKE": ("C0001", 1.00),

        "HEAT": ("C0002", 0.85),

        "DROUGHT": ("C0003", 0.95),

        "INFLATION": ("C0005", 0.90),

        "RECESSION": ("C0005", 0.95),

    }

    def activate(self, event: str):

        event = event.upper()

        for keyword, (constraint, score) in self.RULES.items():

            if keyword in event:

                return ActivatedConstraint(

                    constraint_id=constraint,

                    trigger=keyword,

                    strength=score,

                    source="Rule Engine",

                    evidence=event,

                )

        return None
