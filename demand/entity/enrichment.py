"""
Entity Enrichment Engine.

Transforms candidate spikes into enriched entities ready for
historical reconstruction.
"""

from __future__ import annotations

import duckdb

from demand.entity.resolver_v2 import EntityResolver


class EntityEnrichment:

    def __init__(self, database="data/demand.duckdb"):

        self.con = duckdb.connect(database)

        self.resolver = EntityResolver()

    def initialize(self):

        self.con.execute("""
        CREATE TABLE IF NOT EXISTS enriched_entities(

            asin TEXT PRIMARY KEY,

            title TEXT,

            category TEXT,

            brand TEXT,

            entity TEXT,

            search_query TEXT,

            capability TEXT,

            status TEXT
        )
        """)

    def process(self, limit=100):

        rows = self.con.execute(
            """
            SELECT
                asin,
                title,
                categoryName
            FROM candidate_spikes
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        for asin, title, category in rows:

            result = self.resolver.resolve(
                asin,
                title,
                category,
            )

            self.con.execute(
                """
                INSERT OR REPLACE INTO enriched_entities
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.asin,
                    result.title,
                    result.category,
                    result.brand,
                    result.entity,
                    result.search_query,
                    None,
                    "pending",
                ),
            )
