from __future__ import annotations

import duckdb


class FactorValidator:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def run(self):

        print("\nDuplicates\n")

        print(

            self.con.execute("""

SELECT

event_id,

factor_type,

factor_value,

COUNT(*) c

FROM factor_store

GROUP BY

event_id,

factor_type,

factor_value

HAVING c>1

LIMIT 20

""").fetchdf()

        )

        print("\nNull Values\n")

        print(

            self.con.execute("""

SELECT

SUM(CASE WHEN factor_type IS NULL THEN 1 ELSE 0 END) factor_type_null,

SUM(CASE WHEN factor_value IS NULL THEN 1 ELSE 0 END) factor_value_null,

SUM(CASE WHEN event_id IS NULL THEN 1 ELSE 0 END) event_null

FROM factor_store

""").fetchdf()

        )

        print("\nWeight Range\n")

        print(

            self.con.execute("""

SELECT

MIN(weight),

MAX(weight),

AVG(weight)

FROM factor_store

""").fetchdf()

        )


if __name__ == "__main__":

    FactorValidator().run()
