from demand.replay.database import ReplayDatabase


class HistoricalSpikeLoader:

    def __init__(self):

        self.db = ReplayDatabase()

    def load(self, day):

        return self.db.con.execute(
            """
            SELECT *
            FROM spikes
            WHERE onset_ts=?
            """,
            (
                day,
            ),
        ).fetchdf()
