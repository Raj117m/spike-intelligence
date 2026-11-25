"""
Scientific Experiment Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Experiment:

    name: str

    hypothesis: str

    started: datetime

    status: str = "running"


class ExperimentEngine:

    def __init__(self):

        self.experiments = []

    def start(
        self,
        name: str,
        hypothesis: str,
    ) -> Experiment:

        exp = Experiment(
            name=name,
            hypothesis=hypothesis,
            started=datetime.utcnow(),
        )

        self.experiments.append(exp)

        return exp

    def finish(
        self,
        experiment: Experiment,
        status: str,
    ):

        experiment.status = status
