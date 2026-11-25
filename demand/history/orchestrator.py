from datetime import date

from demand.history.gdelt_archive import GDELTArchive

from demand.history.downloader import Downloader

from demand.history.manifest import Manifest


class HistoryDownloader:

    def __init__(self):

        self.archive = GDELTArchive()

        self.downloader = Downloader()

        self.manifest = Manifest()

    def run(

        self,

        start,

        end,

    ):

        urls = self.archive.build_urls(

            start,

            end,

        )

        completed = 0

        for url in urls:

            filename = url.split("/")[-1]

            if self.manifest.completed(filename):

                continue

            try:

                self.downloader.download(url)

                self.manifest.mark_complete(filename)

                completed += 1

            except Exception as e:

                print(filename)

                print(e)

        print()

        print(

            f"Downloaded {completed} archives."

        )


if __name__ == "__main__":

    HistoryDownloader().run(

        date(2023, 1, 1),

        date(2023, 1, 31),

    )
