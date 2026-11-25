from __future__ import annotations

import duckdb


class SignatureSelector:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        self.con.execute("""
DROP TABLE IF EXISTS production_signatures
""")

        self.con.execute("""

CREATE TABLE production_signatures AS

SELECT

level,

signature,

support,

factor_count,

final_score,

CASE

WHEN factor_count=2 THEN final_score*0.60

WHEN factor_count=3 THEN final_score*0.90

WHEN factor_count>=4 THEN final_score*1.30

END AS prediction_score

FROM signature_library

WHERE

support>=25

AND factor_count>=3

AND signature NOT LIKE '%YEAR=%'

AND signature NOT LIKE '%MONTH=%'

ORDER BY prediction_score DESC

""")

        print()

        print(

            self.con.execute("""

SELECT COUNT(*)

FROM production_signatures

""").fetchdf()

        )

        print()

        print(

            self.con.execute("""

SELECT

level,

COUNT(*)

FROM production_signatures

GROUP BY level

""").fetchdf()

        )

        print()

        print(

            self.con.execute("""

SELECT

signature,

prediction_score,

support

FROM production_signatures

ORDER BY prediction_score DESC

LIMIT 100

""").fetchdf()

        )


if __name__ == "__main__":

    SignatureSelector().build()
