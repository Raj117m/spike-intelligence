from __future__ import annotations

from itertools import combinations

import duckdb
import pandas as pd


class PairMiner:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        self.con.execute("""
DROP TABLE IF EXISTS factor_pairs
""")

        self.con.execute("""
CREATE TABLE factor_pairs(

pair VARCHAR,

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

                    group["factor_type"]
                    + "="
                    + group["factor_value"]

                )

            )

            for pair in combinations(values, 2):

                key = " | ".join(pair)

                support[key] = support.get(key, 0) + 1

            if processed % 5000 == 0:

                print(f"{processed:,} events")

        out = pd.DataFrame(

            [

                {

                    "pair": k,

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

            "pairs",

            out,

        )

        self.con.execute("""

INSERT INTO factor_pairs

SELECT *

FROM pairs

""")

        print()

        print(f"Pairs: {len(out):,}")


if __name__ == "__main__":

    PairMiner().build()
