"""
Generate candidate demand spikes from the Amazon snapshot.
"""

from __future__ import annotations

import duckdb


class SpikeGenerator:

    def __init__(self, database: str = "data/demand.duckdb"):
        self.con = duckdb.connect(database)

    def generate(
        self,
        minimum_reviews: int = 25,
        minimum_monthly_sales: int = 10,
        limit: int = 50000,
    ):

        return self.con.execute(
            """
            SELECT
                asin,
                title,
                categoryName,
                reviews,
                boughtInLastMonth,
                boughtInLastMonth::DOUBLE / (reviews + 1) AS velocity
            FROM amazon_products
            WHERE
                reviews >= ?
                AND boughtInLastMonth >= ?
            ORDER BY velocity DESC
            LIMIT ?
            """,
            (
                minimum_reviews,
                minimum_monthly_sales,
                limit,
            ),
        ).fetchdf()

    def save(self, dataframe):

        self.con.register("candidate_df", dataframe)

        self.con.execute(
            """
            CREATE OR REPLACE TABLE candidate_spikes AS
            SELECT *
            FROM candidate_df
            """
        )

    def stats(self):

        return self.con.execute(
            """
            SELECT
                COUNT(*) AS spikes,
                AVG(velocity) AS average_velocity,
                MAX(velocity) AS max_velocity
            FROM candidate_spikes
            """
        ).fetchdf()
