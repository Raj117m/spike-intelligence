import duckdb


class EvidenceScorer:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def score(self):

        rows = self.con.execute("""

        SELECT

            edge_id,
            support

        FROM evidence_graph

        """).fetchall()

        for edge_id, support in rows:

            support_score = min(support / 100.0, 1.0)

            confidence = support_score

            precision = confidence * 0.95

            self.con.execute("""

            UPDATE evidence_graph

            SET

                confidence=?,

                precision=?

            WHERE edge_id=?

            """,

            (

                confidence,
                precision,
                edge_id

            ))

        print(f"Scored {len(rows):,} graph edges.")


if __name__ == "__main__":

    EvidenceScorer().score()
