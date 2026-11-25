from __future__ import annotations

import duckdb


class EvidenceDatabase:

    def __init__(self):

        self.con = duckdb.connect(
            "data/demand.duckdb"
        )

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS evidence(

            mechanism_id TEXT,

            source TEXT,

            dataset TEXT,

            entity TEXT,

            observation TEXT,

            observed_at TIMESTAMP,

            confidence DOUBLE,

            url TEXT

        )

        """)

    def save(self, evidence):

        self.con.execute(

        """
        INSERT INTO evidence
        VALUES (?,?,?,?,?,?,?,?)
        """,

        (

            evidence.mechanism_id,

            evidence.source,

            evidence.dataset,

            evidence.entity,

            evidence.observation,

            evidence.observed_at,

            evidence.confidence,

            evidence.url,

        )

        )

    def all(self):

        return self.con.execute(

            """

            SELECT *

            FROM evidence

            ORDER BY observed_at DESC

            """

        ).fetchdf()
