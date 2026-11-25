"""
Persistence layer for Adaptive Market Science.
"""

from __future__ import annotations

import duckdb

from demand.scientist.variable import LatentVariable


class ScientistDatabase:

    def __init__(self, path: str = "data/demand.duckdb"):

        self.con = duckdb.connect(path)

    def initialize(self):

        self.con.execute("""
        CREATE TABLE IF NOT EXISTS latent_variables (

            name TEXT PRIMARY KEY,

            definition TEXT,

            confidence DOUBLE,

            evidence_count INTEGER,

            validated BOOLEAN,

            notes TEXT
        )
        """)

    def save_variable(self, variable: LatentVariable):

        self.con.execute("""
        INSERT OR REPLACE INTO latent_variables
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            variable.name,
            variable.definition,
            variable.confidence,
            variable.evidence_count,
            variable.validated,
            variable.notes,
        ))

    def variables(self):

        return self.con.execute(
            "SELECT * FROM latent_variables"
        ).fetchall()
