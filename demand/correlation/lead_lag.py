import duckdb


class LeadLagEngine:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        return self.con.execute("""

        SELECT

            e.observation_type,

            s.segment,

            COUNT(*) support

        FROM environmental_observations e

        JOIN spikes s

        ON e.observed_at <= s.onset_ts

        GROUP BY

            e.observation_type,

            s.segment

        ORDER BY support DESC

        """).fetchdf()
