import duckdb


class GraphDatabase:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS evidence_graph(

            edge_id UUID DEFAULT uuid(),

            factor VARCHAR,

            mechanism VARCHAR,

            category VARCHAR,

            support INTEGER,

            confidence DOUBLE,

            precision DOUBLE,

            avg_lead_days DOUBLE,

            false_positives INTEGER,

            first_seen DATE,

            last_seen DATE,

            last_validated TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

    def stats(self):

        return self.con.execute("""

        SELECT

            COUNT(*) edges

        FROM evidence_graph

        """).fetchdf()
