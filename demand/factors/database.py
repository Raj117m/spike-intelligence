from __future__ import annotations

import duckdb


class FactorDatabase:

    def __init__(
        self,
        database="data/demand.duckdb",
    ):

        self.con = duckdb.connect(database)

    def create(self):

        self.con.execute(
            """

CREATE TABLE IF NOT EXISTS factor_store(

    factor_id BIGINT,

    event_id VARCHAR,

    observed_at DATE,

    factor_type VARCHAR,

    factor_value VARCHAR,

    weight DOUBLE

);

"""
        )

        self.con.execute(
            """

CREATE INDEX IF NOT EXISTS idx_factor_event
ON factor_store(event_id);

"""
        )

        self.con.execute(
            """

CREATE INDEX IF NOT EXISTS idx_factor_date
ON factor_store(observed_at);

"""
        )

        self.con.execute(
            """

CREATE INDEX IF NOT EXISTS idx_factor_type
ON factor_store(factor_type);

"""
        )

        self.con.execute(
            """

CREATE INDEX IF NOT EXISTS idx_factor_value
ON factor_store(factor_value);

"""
        )

    def truncate(self):

        self.con.execute(
            "DELETE FROM factor_store"
        )

    def insert_dataframe(
        self,
        dataframe,
    ):

        self.con.register(
            "temp_df",
            dataframe,
        )

        self.con.execute(
            """

INSERT INTO factor_store

SELECT *

FROM temp_df

"""
        )

    def count(self):

        return self.con.execute(
            """

SELECT COUNT(*)

FROM factor_store

"""
        ).fetchone()[0]
