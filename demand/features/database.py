from __future__ import annotations

import duckdb


class FeatureDatabase:

    def __init__(self):

        self.con = duckdb.connect(
            "data/demand.duckdb"
        )

    def create(self):

        self.con.execute("""

CREATE TABLE IF NOT EXISTS daily_feature_store(

feature_date DATE,

factor_type VARCHAR,

factor_value VARCHAR,

event_count BIGINT,

total_weight DOUBLE,

avg_weight DOUBLE

)

""")

        self.con.execute("""

CREATE TABLE IF NOT EXISTS rolling_feature_store(

feature_date DATE,

window_days INTEGER,

factor_type VARCHAR,

factor_value VARCHAR,

rolling_events BIGINT,

rolling_weight DOUBLE,

rolling_avg DOUBLE

)

""")
