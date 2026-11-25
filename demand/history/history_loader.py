from pathlib import Path

from demand.history.parser import HistoricalParser
from demand.environment.gdelt_ingestor import GDELTIngestor


class HistoryLoader:

    def __init__(self):

        self.parser = HistoricalParser()

        self.ingestor = GDELTIngestor()

    def ingest_archive(self, archive: Path):

        df = self.parser.parse(archive)

        print()

        print(archive.name)

        print("Rows :", len(df))

        self.ingestor.ingest_dataframe(df)
