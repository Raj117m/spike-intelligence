"""
Dataset Fetcher.

Downloads official datasets from the registry.
"""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import duckdb


class DatasetFetcher:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

        self.root = Path("data_lake/raw")

        self.root.mkdir(parents=True, exist_ok=True)

    def fetch(self, dataset_id: str):

        row = self.con.execute(
            """
            SELECT
                id,
                download
            FROM datasets
            WHERE id=?
            """,
            (dataset_id,),
        ).fetchone()

        if row is None:
            raise ValueError(dataset_id)

        _, url = row

        filename = url.rstrip("/").split("/")[-1]

        if filename == "":
            raise RuntimeError(
                "Dataset points to a directory. Use a concrete file URL."
            )

        destination = self.root / filename

        if destination.exists():

            print("Already downloaded.")

            return destination

        print("Downloading:", url)

        urllib.request.urlretrieve(url, destination)

        print("Finished.")

        return destination

    @staticmethod
    def sha256(path):

        h = hashlib.sha256()

        with open(path, "rb") as f:

            while True:

                block = f.read(1024 * 1024)

                if not block:
                    break

                h.update(block)

        return h.hexdigest()
