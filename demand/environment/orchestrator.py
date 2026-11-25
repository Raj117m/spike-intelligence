from pathlib import Path

from demand.environment.gdelt_ingestor import GDELTIngestor


class ObservationOrchestrator:

    def __init__(self):

        self.ingestors = [

            GDELTIngestor(),

        ]

    def run(self):

        print()

        print("=== ENVIRONMENT UPDATE ===")

        print()

        gdelt = Path(
            "data_lake/raw/gdelt/20260630.export.CSV.zip"
        )

        if gdelt.exists():

            print("Running GDELT...")

            self.ingestors[0].ingest(gdelt)

        else:

            print("No GDELT file found.")

        print()

        print("Update complete.")
