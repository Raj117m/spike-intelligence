from __future__ import annotations

import duckdb


class EntityStore:

    def __init__(self, database="data/demand.duckdb"):

        self.con = duckdb.connect(database)

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS canonical_entities(

            asin TEXT PRIMARY KEY,

            canonical_name TEXT,

            wikipedia_title TEXT,

            wikidata_id TEXT,

            manufacturer TEXT,

            confidence DOUBLE

        )

        """)
