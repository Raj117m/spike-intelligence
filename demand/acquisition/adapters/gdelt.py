from __future__ import annotations

import hashlib
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from demand.acquisition.adapters.base import DatasetAdapter


class GDELTAdapter(DatasetAdapter):

    ROOT = "http://data.gdeltproject.org/events/"

    def latest_version(self):

        html = requests.get(
            self.ROOT,
            timeout=60,
            headers={
                "User-Agent": "DemandPhysicsResearchBot/1.0"
            },
        ).text

        soup = BeautifulSoup(html, "html.parser")

        files = []

        for link in soup.find_all("a"):

            href = link.get("href", "")

            if re.fullmatch(r"\d{8}\.export\.CSV\.zip", href):

                files.append(href)

        files.sort()

        return files[-1]

    def check(self):

        return self.latest_version()

    def download(self):

        filename = self.latest_version()

        url = self.ROOT + filename

        destination = Path("data_lake/raw/gdelt")

        destination.mkdir(parents=True, exist_ok=True)

        outfile = destination / filename

        if outfile.exists():

            print("Already downloaded.")

            return outfile

        print("Downloading")

        r = requests.get(
            url,
            stream=True,
            timeout=600,
            headers={
                "User-Agent": "DemandPhysicsResearchBot/1.0"
            },
        )

        r.raise_for_status()

        with open(outfile, "wb") as f:

            for chunk in r.iter_content(1024 * 1024):

                if chunk:

                    f.write(chunk)

        print("Finished")

        return outfile

    def verify(self):

        path = self.download()

        h = hashlib.sha256()

        with open(path, "rb") as f:

            while True:

                block = f.read(1024 * 1024)

                if not block:
                    break

                h.update(block)

        checksum = h.hexdigest()

        print(checksum)

        return checksum

    def normalize(self):

        raise NotImplementedError

    def metadata(self):

        return {
            "dataset": "GDELT",
            "latest": self.latest_version(),
        }
