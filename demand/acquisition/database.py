from __future__ import annotations

import duckdb


class DatasetDatabase:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS datasets(

            id TEXT PRIMARY KEY,

            name TEXT,

            organization TEXT,

            source_type TEXT,

            homepage TEXT,

            download TEXT,

            update_frequency TEXT,

            historical_start TEXT,

            format TEXT,

            estimated_size_gb DOUBLE,

            license TEXT,

            priority DOUBLE,

            enabled BOOLEAN

        )

        """)
