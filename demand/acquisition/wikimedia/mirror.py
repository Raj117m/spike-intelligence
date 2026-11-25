"""
Mirror Wikimedia dumps locally.

Downloads official dump files and skips downloads if they already exist.
"""

from __future__ import annotations

from pathlib import Path
import urllib.request


class WikimediaMirror:

    BASE = "https://dumps.wikimedia.org/other/pageview_complete/monthly/"

    def __init__(self):

        self.root = Path("data_lake/raw/wikimedia")

        self.root.mkdir(parents=True, exist_ok=True)

    def download(self, filename: str):

        destination = self.root / filename

        if destination.exists():

            print("Already downloaded:", destination)

            return destination

        url = self.BASE + filename

        print("Downloading")

        print(url)

        urllib.request.urlretrieve(url, destination)

        print("Finished")

        return destination
