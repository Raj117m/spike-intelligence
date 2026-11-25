from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Experiment:

    id: str
    question: str
    hypothesis: str
    status: str
    created: datetime


class ExperimentRegistry:

    def __init__(self):
        self._experiments = {}

    def register(self, experiment: Experiment):

        self._experiments[experiment.id] = experiment

    def get(self, experiment_id: str):

        return self._experiments[experiment_id]

    def all(self):

        return list(self._experiments.values())
