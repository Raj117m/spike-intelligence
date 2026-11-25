"""
Dataset Mirror Manager.

Keeps track of mirrored datasets.
"""

from __future__ import annotations

import duckdb
from datetime import datetime


class MirrorManager:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS mirrors(

            dataset_id TEXT,

            version TEXT,

            mirrored_at TIMESTAMP,

            checksum TEXT,

            size_bytes BIGINT,

            status TEXT

        )

        """)

    def register(
        self,
        dataset_id,
        version,
        checksum="",
        size_bytes=0,
        status="completed",
    ):

        self.con.execute(

            """
            INSERT INTO mirrors
            VALUES (?,?,?,?,?,?)
            """,

            (
                dataset_id,
                version,
                datetime.utcnow(),
                checksum,
                size_bytes,
                status,
            ),
        )

    def history(self):

        return self.con.execute("""

        SELECT *

        FROM mirrors

        ORDER BY mirrored_at DESC

        """).fetchdf()
