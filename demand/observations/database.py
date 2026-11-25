import duckdb


class ObservationDatabase:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS observations(

            source TEXT,

            observation_type TEXT,

            entity TEXT,

            location TEXT,

            value VARCHAR,

            unit TEXT,

            observed_at TIMESTAMP,

            confidence DOUBLE,

            raw_source TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

    def insert(
        self,
        observation,
    ):

        self.con.execute(
            """

            INSERT INTO observations

            VALUES(

                ?,?,?,?,?,?,?,?,?,
                CURRENT_TIMESTAMP

            )

            """,
            (

                observation.source,

                observation.observation_type,

                observation.entity,

                observation.location,

                str(observation.value),

                observation.unit,

                observation.observed_at,

                observation.confidence,

                observation.raw_source,

            ),
        )

    def count(self):

        return self.con.execute(

            "SELECT COUNT(*) FROM observations"

        ).fetchone()[0]
