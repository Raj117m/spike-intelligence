from __future__ import annotations

from pathlib import Path

from demand.acquisition.registry import SourceRegistry
from demand.acquisition.downloader import Downloader


class AcquisitionScheduler:

    def __init__(self):

        self.registry = SourceRegistry()

        self.downloader = Downloader()

    def run(self):

        for source in self.registry.all():

            if not source.enabled:
                continue

            print(f"\nChecking {source.id}")

            if not source.download_url:

                print("No downloader configured.")

                continue

            filename = source.download_url.split("/")[-1]

            destination = Path(
                "data_lake/raw"
            ) / source.storage_folder / filename

            self.downloader.download(
                source.download_url,
                destination,
            )

            checksum = self.downloader.sha256(destination)

            print("Downloaded")

            print(destination)

            print(checksum)
