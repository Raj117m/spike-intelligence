import duckdb


class CorrelationDatabase:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS factor_correlations(

            correlation_id UUID DEFAULT uuid(),

            factor VARCHAR,

            product_category VARCHAR,

            lead_days INTEGER,

            support INTEGER,

            confidence DOUBLE,

            lift DOUBLE,

            precision DOUBLE,

            recall DOUBLE,

            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

    def stats(self):

        return self.con.execute("""

        SELECT

            COUNT(*) correlations

        FROM factor_correlations

        """).fetchdf()
