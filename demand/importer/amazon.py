from __future__ import annotations

import duckdb

from .base import Importer


class AmazonImporter(Importer):

    def __init__(
        self,
        csv_path: str,
        db_path: str = "data/demand.duckdb",
    ) -> None:

        self.csv_path = csv_path
        self.db_path = db_path

    def import_data(self) -> None:

        con = duckdb.connect(self.db_path)

        con.execute(f"""
        CREATE OR REPLACE TABLE amazon_products AS
        SELECT *
        FROM read_csv_auto('{self.csv_path}')
        """)

        count = con.execute(
            "SELECT COUNT(*) FROM amazon_products"
        ).fetchone()[0]

        print(f"Imported {count:,} Amazon products.")
