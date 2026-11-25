import duckdb


class WindowedLeadEngine:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def build(self, window_days=60):

        query = f"""
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
            ) AS avg_lead_days,

            MIN(
                DATE_DIFF(
                    'day',
                    e.observed_at,
                    s.onset_ts
                )
            ) AS min_lead_days,

            MAX(
                DATE_DIFF(
                    'day',
                    e.observed_at,
                    s.onset_ts
                )
            ) AS max_lead_days

        FROM spikes s

        JOIN environmental_observations e

        ON e.observed_at BETWEEN
            s.onset_ts - INTERVAL '{window_days} days'
            AND s.onset_ts

        GROUP BY

            s.product_id,
            s.segment,
            e.observation_type

        HAVING COUNT(*) >= 2

        ORDER BY

            support DESC,
            avg_lead_days ASC
        """

        return self.con.execute(query).fetchdf()
