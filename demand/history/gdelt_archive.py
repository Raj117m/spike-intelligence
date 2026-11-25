from datetime import date
from datetime import timedelta


class GDELTArchive:

    BASE = "http://data.gdeltproject.org/events"

    def build_urls(

        self,

        start,

        end,

    ):

        current = start

        urls = []

        while current <= end:

            urls.append(

                f"{self.BASE}/"

                f"{current.strftime('%Y%m%d')}"

                ".export.CSV.zip"

            )

            current += timedelta(days=1)

        return urls
