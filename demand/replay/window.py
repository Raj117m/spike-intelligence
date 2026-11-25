from datetime import timedelta


class ReplayWindowGenerator:

    def __init__(self, config):

        self.config = config

    def generate(self):

        current = self.config.replay_start

        while current <= self.config.replay_end:

            yield {

                "window_start": current -

                timedelta(days=self.config.window_days),

                "window_end": current,

                "prediction_day": current,

            }

            current += timedelta(days=self.config.step_days)
