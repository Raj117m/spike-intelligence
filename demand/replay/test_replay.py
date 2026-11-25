from datetime import date

from demand.replay.config import ReplayConfig
from demand.replay.replay_engine import ReplayEngine


config = ReplayConfig(

    replay_start=date(2023, 9, 1),

    replay_end=date(2023, 9, 15),

)

state = ReplayEngine(config).run()

print()

print(state.windows)
