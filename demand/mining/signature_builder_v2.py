from __future__ import annotations

import duckdb


class SignatureBuilder:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        self.con.execute("""
DROP TABLE IF EXISTS learned_signatures
""")

        self.con.execute("""

CREATE TABLE learned_signatures AS

SELECT

'PAIR' AS level,
pair AS signature,
support,
support*1.0 AS score

FROM factor_pairs

UNION ALL

SELECT

'TRIPLE',
triple,
support,
support*1.5

FROM factor_triples

UNION ALL

SELECT

'QUAD',
quad,
support,
support*2.0

FROM factor_quads

""")

        print()

        print(

            self.con.execute("""

SELECT
level,
COUNT(*)

FROM learned_signatures

GROUP BY level

""").fetchdf()

        )

        print()

        print(

            self.con.execute("""

SELECT *

FROM learned_signatures

ORDER BY score DESC

LIMIT 100

""").fetchdf()

        )


if __name__ == "__main__":

    SignatureBuilder().build()
