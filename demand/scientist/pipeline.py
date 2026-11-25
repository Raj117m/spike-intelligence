"""
Scientific estimation pipeline.
"""

from demand.scientist.variable import VariableRegistry
from demand.scientist.state import StateEstimator


class ScientistPipeline:

    def __init__(self):

        self.registry = VariableRegistry()

        self.estimator = StateEstimator()

    def run(self):

        variables = self.registry.all()

        return self.estimator.estimate(variables)
