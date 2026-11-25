from __future__ import annotations

from itertools import combinations

import duckdb
import pandas as pd


class QuadMiner:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        self.con.execute("""
DROP TABLE IF EXISTS factor_quads
""")

        self.con.execute("""
CREATE TABLE factor_quads(

quad VARCHAR,

support INTEGER

)
""")

        df = self.con.execute("""

SELECT
event_id,
factor_type,
factor_value

FROM factor_store

ORDER BY event_id

""").fetchdf()

        grouped = df.groupby("event_id")

        support = {}

        processed = 0

        for event_id, group in grouped:

            processed += 1

            values = sorted(
                set(
                    group["factor_type"] + "=" + group["factor_value"]
                )
            )

            if len(values) < 4:
                continue

            for quad in combinations(values, 4):

                key = " | ".join(quad)

                support[key] = support.get(key, 0) + 1

            if processed % 5000 == 0:

                print(f"{processed:,} events")

        out = pd.DataFrame(

            [
                {
                    "quad": k,
                    "support": v,
                }
                for k, v in support.items()
            ]

        )

        out = out.sort_values(
            "support",
            ascending=False,
        )

        self.con.register(
            "quads",
            out,
        )

        self.con.execute("""

INSERT INTO factor_quads

SELECT *

FROM quads

""")

        print()

        print(f"Quads: {len(out):,}")


if __name__ == "__main__":

    QuadMiner().build()
