from __future__ import annotations

import duckdb


class ConstraintDatabase:

    def __init__(self):

        self.con = duckdb.connect(
            "data/demand.duckdb"
        )

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS constraints(

            id TEXT PRIMARY KEY,

            name TEXT,

            category TEXT,

            description TEXT,

            physical_domain TEXT,

            confidence DOUBLE,

            validated BOOLEAN

        )

        """)

    def save(self, c):

        self.con.execute(

        """

        INSERT OR REPLACE INTO constraints

        VALUES (?,?,?,?,?,?,?)

        """,

        (

            c.id,

            c.name,

            c.category,

            c.description,

            c.physical_domain,

            c.confidence,

            c.validated,

        )

        )

    def all(self):

        return self.con.execute(

        """

        SELECT *

        FROM constraints

        ORDER BY confidence DESC

        """

        ).fetchdf()
