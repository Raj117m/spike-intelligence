import duckdb
import uuid


class SignatureBuilder:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        self.con.execute("DELETE FROM signatures")

        rows = self.con.execute("""

        SELECT

            factor,
            category,
            mechanism,
            COUNT(*) support

        FROM evidence_graph

        GROUP BY

            factor,
            category,
            mechanism

        HAVING COUNT(*) >= 1
        ORDER BY support DESC

        """).fetchall()

        inserted = 0

        for factor, category, mechanism, support in rows:

            self.con.execute("""

            INSERT INTO signatures(

                signature_id,
                factor_set,
                category_scope,
                lag_dist,
                hit_rate,
                support_n

            )

            VALUES(

                ?,?,?,?,?,?

            )

            """, (

                str(uuid.uuid4()),
                f"{factor}|{mechanism}",
                category,
                "UNKNOWN",
                0.50,
                support

            ))

            inserted += 1

        print(f"Built {inserted:,} signatures.")


if __name__ == "__main__":

    SignatureBuilder().build()
