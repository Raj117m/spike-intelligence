from pathlib import Path

import hashlib
import requests


class Downloader:

    def download(self, url: str, destination: Path):

        destination.parent.mkdir(parents=True, exist_ok=True)

        r = requests.get(url, stream=True, timeout=120)

        r.raise_for_status()

        with open(destination, "wb") as f:

            for chunk in r.iter_content(1024 * 1024):

                if chunk:

                    f.write(chunk)

        return destination

    def sha256(self, path: Path):

        h = hashlib.sha256()

        with open(path, "rb") as f:

            while True:

                b = f.read(1024 * 1024)

                if not b:
                    break

                h.update(b)

        return h.hexdigest()
