import duckdb


class PredictionValidator:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def validate(self):

        rows = self.con.execute("""

        SELECT

            pred_id,
            segment

        FROM predictions

        """).fetchall()

        validated = 0

        correct = 0

        for pred_id, segment in rows:

            hit = self.con.execute("""

            SELECT COUNT(*)

            FROM spikes

            WHERE segment=?

            """, (segment,)).fetchone()[0]

            validated += 1

            if hit:

                correct += 1

                self.con.execute("""

                UPDATE predictions

                SET status='HIT'

                WHERE pred_id=?

                """, (pred_id,))

            else:

                self.con.execute("""

                UPDATE predictions

                SET status='MISS'

                WHERE pred_id=?

                """, (pred_id,))

        print()

        print("Validated :", validated)

        print("Hits      :", correct)

        print("Accuracy  :", round(correct/max(validated,1),3))
