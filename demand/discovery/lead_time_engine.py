import duckdb


class LeadTimeEngine:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        return self.con.execute("""

        SELECT

            s.product_id,

            s.segment,

            e.observation_type,

            COUNT(*) AS support,

            AVG(
                DATE_DIFF(
                    'day',
                    e.observed_at,
                    s.onset_ts
                )
            ) AS avg_lead_days

        FROM spikes s

        JOIN environmental_observations e

        ON e.observed_at <= s.onset_ts

        GROUP BY

            s.product_id,
            s.segment,
            e.observation_type

        HAVING support >= 3

        ORDER BY

            support DESC,
            avg_lead_days ASC

        """).fetchdf()
