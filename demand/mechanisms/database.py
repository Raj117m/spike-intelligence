from __future__ import annotations

import duckdb


class MechanismDatabase:

    def __init__(self):

        self.con = duckdb.connect(
            "data/demand.duckdb"
        )

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS mechanisms(

            id TEXT PRIMARY KEY,

            name TEXT,

            description TEXT,

            trigger TEXT,

            latent_state TEXT,

            capability TEXT,

            outcome TEXT,

            confidence DOUBLE,

            validated BOOLEAN

        )

        """)

    def save(self, mechanism):

        self.con.execute(

        """
        INSERT OR REPLACE INTO mechanisms
        VALUES (?,?,?,?,?,?,?,?,?)
        """,

        (

            mechanism.id,

            mechanism.name,

            mechanism.description,

            mechanism.trigger,

            mechanism.latent_state,

            mechanism.capability,

            mechanism.outcome,

            mechanism.confidence,

            mechanism.validated,

        )

        )

    def all(self):

        return self.con.execute(

            """

            SELECT *

            FROM mechanisms

            ORDER BY confidence DESC

            """

        ).fetchdf()
