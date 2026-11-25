from __future__ import annotations

import duckdb


class DailyAggregator:

    def __init__(self):

        self.con = duckdb.connect(
            "data/demand.duckdb"
        )

    def build(self):

        print()
        print("Building daily feature store...")
        print()

        self.con.execute("""

DELETE FROM daily_feature_store

""")

        self.con.execute("""

INSERT INTO daily_feature_store

SELECT

observed_at AS feature_date,

factor_type,

factor_value,

COUNT(*) AS event_count,

SUM(weight) AS total_weight,

AVG(weight) AS avg_weight

FROM factor_store

GROUP BY

observed_at,

factor_type,

factor_value

""")
