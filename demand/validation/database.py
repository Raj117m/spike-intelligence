import duckdb


class ValidationDatabase:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS prediction_validations(

            validation_id UUID DEFAULT uuid(),

            prediction_id VARCHAR,

            product_id VARCHAR,

            predicted_probability DOUBLE,

            actual_outcome BOOLEAN,

            prediction_error DOUBLE,

            missing_factor VARCHAR,

            explanation VARCHAR,

            validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

    def stats(self):

        return self.con.execute("""

        SELECT

            COUNT(*) validations,

            AVG(prediction_error) avg_error

        FROM prediction_validations

        """).fetchdf()
