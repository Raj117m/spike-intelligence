import duckdb


class EnvironmentalObservationDatabase:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS environmental_observations(

            observation_id UUID DEFAULT uuid(),

            source VARCHAR,

            source_record_id VARCHAR,

            observation_type VARCHAR,

            entity VARCHAR,

            location VARCHAR,

            latitude DOUBLE,

            longitude DOUBLE,

            value VARCHAR,

            numeric_value DOUBLE,

            unit VARCHAR,

            confidence DOUBLE,

            observed_at TIMESTAMP,

            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            raw_payload VARCHAR

        )

        """)

    def stats(self):

        return self.con.execute("""

        SELECT

            COUNT(*) observations,

            COUNT(DISTINCT source) sources,

            COUNT(DISTINCT observation_type) observation_types

        FROM environmental_observations

        """).fetchdf()
