from __future__ import annotations

import duckdb


class FactorStatistics:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def summary(self):

        print("\n========== FACTOR STORE ==========\n")

        print(

            self.con.execute("""

SELECT COUNT(*)

FROM factor_store

""").fetchdf()

        )

        print("\n========== FACTOR TYPES ==========\n")

        print(

            self.con.execute("""

SELECT

factor_type,

COUNT(*) total,

ROUND(AVG(weight),2) avg_weight

FROM factor_store

GROUP BY factor_type

ORDER BY total DESC

""").fetchdf()

        )

        print("\n========== TOP FACTORS ==========\n")

        print(

            self.con.execute("""

SELECT

factor_type,

factor_value,

COUNT(*) support

FROM factor_store

GROUP BY factor_type,factor_value

ORDER BY support DESC

LIMIT 100

""").fetchdf()

        )

        print("\n========== DAILY EVENTS ==========\n")

        print(

            self.con.execute("""

SELECT

observed_at,

COUNT(*) total

FROM factor_store

GROUP BY observed_at

ORDER BY observed_at

LIMIT 30

""").fetchdf()

        )

        print("\n========== UNIQUE VALUES ==========\n")

        print(

            self.con.execute("""

SELECT

factor_type,

COUNT(DISTINCT factor_value) unique_values

FROM factor_store

GROUP BY factor_type

ORDER BY unique_values DESC

""").fetchdf()

        )


if __name__ == "__main__":

    FactorStatistics().summary()
