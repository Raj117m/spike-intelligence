"""
Ontology Builder

Creates and manages the validated Demand Physics ontology.
"""

from __future__ import annotations

import duckdb


class OntologyBuilder:

    def __init__(self, db_path: str = "data/demand.duckdb") -> None:
        self.con = duckdb.connect(db_path)

    def initialize(self) -> None:

        self.con.execute("""
        CREATE TABLE IF NOT EXISTS ontology_nodes (

            node_id VARCHAR PRIMARY KEY,

            node_type VARCHAR,

            name VARCHAR,

            description VARCHAR,

            created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.con.execute("""
        CREATE TABLE IF NOT EXISTS ontology_edges (

            edge_id VARCHAR,

            source_node VARCHAR,

            target_node VARCHAR,

            relationship VARCHAR,

            confidence DOUBLE,

            evidence_count INTEGER,

            contradiction_count INTEGER,

            avg_lead_days DOUBLE,

            precision DOUBLE,

            last_validated TIMESTAMP,

            PRIMARY KEY(edge_id)

        )
        """)

        print("Ontology initialized.")
