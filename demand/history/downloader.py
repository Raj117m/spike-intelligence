from pathlib import Path
import requests


class Downloader:

    def __init__(self):

        self.root = Path("data_lake/raw/gdelt_history")

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def download(self, url):

        filename = url.split("/")[-1]

        target = self.root / filename

        if target.exists():

            print("Already downloaded")

            return target

        print("Downloading")

        r = requests.get(
            url,
            timeout=120,
            stream=True,
        )

        r.raise_for_status()

        with open(target, "wb") as f:

            for chunk in r.iter_content(1024 * 1024):

                if chunk:

                    f.write(chunk)

        return target
