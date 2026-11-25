import duckdb


class SignatureEvolution:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def evolve(self):

        rows = self.con.execute("""
            SELECT
                signature_id,
                hit_rate,
                support_n
            FROM signatures
        """).fetchall()

        updated = 0

        for signature_id, hit_rate, support_n in rows:

            result = self.con.execute("""
                SELECT
                    SUM(CASE WHEN status='HIT' THEN 1 ELSE 0 END) AS hits,
                    SUM(CASE WHEN status='MISS' THEN 1 ELSE 0 END) AS misses
                FROM predictions
                WHERE signature_id=?
            """, (signature_id,)).fetchone()

            hits = result[0] or 0
            misses = result[1] or 0

            total = hits + misses

            if total == 0:
                continue

            new_hit_rate = hits / total

            self.con.execute("""
                UPDATE signatures
                SET
                    hit_rate=?,
                    support_n=?
                WHERE signature_id=?
            """, (
                new_hit_rate,
                support_n + hits,
                signature_id,
            ))

            updated += 1

        print(f"Updated {updated} signatures.")


if __name__ == "__main__":
    SignatureEvolution().evolve()
