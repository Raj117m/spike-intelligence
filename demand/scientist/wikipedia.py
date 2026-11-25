"""
Wikipedia Attention Sensor.
"""

from __future__ import annotations

import duckdb


class WikipediaSensor:

    def __init__(self, path="data/demand.duckdb"):

        self.con = duckdb.connect(path)

    def pageviews(self, topic: str):

        return self.con.execute(
            """
            SELECT ts, views
            FROM pageviews
            WHERE topic = ?
            ORDER BY ts
            """,
            (topic,),
        ).fetchall()
