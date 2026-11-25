from demand.replay.database import ReplayDatabase


class HistoricalEnvironmentLoader:

    def __init__(self):

        self.db = ReplayDatabase()

    def load(self, start_date, end_date):

        return self.db.con.execute(
            """
            SELECT *
            FROM environmental_observations
            WHERE observed_at
            BETWEEN ? AND ?
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchdf()
