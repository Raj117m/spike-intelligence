import duckdb


class TimelineCorrelator:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def observation_counts(self):

        return self.con.execute("""

        SELECT

            observation_type,

            COUNT(*) observations,

            MIN(observed_at) first_seen,

            MAX(observed_at) last_seen

        FROM environmental_observations

        GROUP BY observation_type

        ORDER BY observations DESC

        """).fetchdf()

    def spike_counts(self):

        return self.con.execute("""

        SELECT

            COUNT(*) spikes

        FROM spikes

        """).fetchdf()
