from demand.acquisition.source import Source
from demand.sources.imd import IMD


class SourceRegistry:

    def all(self):

        return [

            Source(

                id="GDELT",

                name="GDELT Events",

                homepage="https://www.gdeltproject.org",

                download_url="http://data.gdeltproject.org/events/20260630.export.CSV.zip",

                update_frequency="15min",

                format="zip",

                storage_folder="gdelt",

            ),

            IMD,

            Source(

                id="CWC",

                name="Central Water Commission",

                homepage="https://rsms.cwc.gov.in",

                download_url="",

                update_frequency="weekly",

                format="pdf",

                storage_folder="cwc",

            ),

        ]
