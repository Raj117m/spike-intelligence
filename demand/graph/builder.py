import duckdb


class EvidenceGraphBuilder:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        rows = self.con.execute("""

        SELECT

            observation_type,

            segment,

            COUNT(*) support

        FROM environmental_observations e

        JOIN spikes s

        ON e.observed_at <= s.onset_ts

        GROUP BY

            observation_type,

            segment

        ORDER BY support DESC

        """).fetchall()

        self.con.execute("DELETE FROM evidence_graph")

        for observation, segment, support in rows:

            self.con.execute("""

            INSERT INTO evidence_graph(

                factor,

                mechanism,

                category,

                support,

                confidence,

                precision,

                avg_lead_days,

                false_positives,

                first_seen,

                last_seen

            )

            VALUES(

                ?,?,?,?,?,?,?,?,?,?

            )

            """,

            (

                observation,

                "UNKNOWN",

                segment,

                support,

                0.50,

                0.50,

                None,

                0,

                None,

                None

            ))
