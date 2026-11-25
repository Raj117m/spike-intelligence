from demand.replay.environment_loader import HistoricalEnvironmentLoader
from demand.replay.spike_loader import HistoricalSpikeLoader
from demand.replay.signature_loader import SignatureLoader
from demand.replay.window import ReplayWindowGenerator
from demand.replay.state import ReplayState


class ReplayEngine:

    def __init__(self, config):

        self.config = config

        self.windows = ReplayWindowGenerator(config)

        self.environment = HistoricalEnvironmentLoader()

        self.spikes = HistoricalSpikeLoader()

        self.signatures = SignatureLoader()

        self.state = ReplayState()

    def run(self):

        signatures = self.signatures.load()

        for window in self.windows.generate():

            env = self.environment.load(

                window["window_start"],

                window["window_end"]

            )

            spikes = self.spikes.load(

                window["prediction_day"]

            )

            print("=" * 80)

            print(window["prediction_day"])

            print("Environment :", len(env))

            print("Spikes      :", len(spikes))

            print("Signatures  :", len(signatures))

            self.state.windows += 1

        return self.state
