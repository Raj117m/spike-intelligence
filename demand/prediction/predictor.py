import duckdb
import uuid
from datetime import datetime, timedelta


class Predictor:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def run(self):

        self.con.execute("DELETE FROM predictions")

        rows = self.con.execute("""
            SELECT
                signature_id,
                factor_set,
                category_scope,
                hit_rate
            FROM signatures
        """).fetchall()

        inserted = 0

        today = datetime.utcnow().date()

        for signature_id, factor_set, category, hit_rate in rows:

            self.con.execute("""
                INSERT INTO predictions(
                    pred_id,
                    product_id,
                    segment,
                    made_ts,
                    window_start,
                    window_end,
                    prob,
                    signature_id,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                None,
                category,
                datetime.utcnow(),
                today,
                today + timedelta(days=30),
                hit_rate,
                signature_id,
                "ACTIVE"
            ))

            inserted += 1

        print(f"Created {inserted:,} predictions.")


if __name__ == "__main__":
    Predictor().run()
