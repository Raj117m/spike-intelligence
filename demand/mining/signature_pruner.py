from __future__ import annotations

import duckdb


class SignaturePruner:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def prune(self):

        self.con.execute("""
DROP TABLE IF EXISTS signature_library
""")

        self.con.execute("""

CREATE TABLE signature_library AS

SELECT

level,

signature,

support,

score,

length(signature)-length(replace(signature,'|',''))+1
AS factor_count

FROM learned_signatures

WHERE support>=10

""")

        self.con.execute("""

ALTER TABLE signature_library

ADD COLUMN rarity DOUBLE

""")

        self.con.execute("""

UPDATE signature_library

SET rarity=

score/support

""")

        self.con.execute("""

ALTER TABLE signature_library

ADD COLUMN final_score DOUBLE

""")

        self.con.execute("""

UPDATE signature_library

SET final_score=

(score*0.70)+
(rarity*0.30)

""")

        print()

        print(

            self.con.execute("""

SELECT COUNT(*)

FROM signature_library

""").fetchdf()

        )

        print()

        print(

            self.con.execute("""

SELECT

level,

COUNT(*)

FROM signature_library

GROUP BY level

""").fetchdf()

        )

        print()

        print(

            self.con.execute("""

SELECT

level,

factor_count,

AVG(final_score) avg_score

FROM signature_library

GROUP BY

level,

factor_count

ORDER BY

level,

factor_count

""").fetchdf()

        )

        print()

        print(

            self.con.execute("""

SELECT

level,

signature,

support,

final_score

FROM signature_library

ORDER BY

final_score DESC

LIMIT 100

""").fetchdf()

        )


if __name__ == "__main__":

    SignaturePruner().prune()
