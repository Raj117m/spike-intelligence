from pathlib import Path
from datetime import datetime

import pandas as pd

from demand.environment.classifier import EnvironmentalClassifier
from demand.environment.database import EnvironmentalObservationDatabase
from demand.environment.loader import ObservationLoader
from demand.environment.models import EnvironmentalObservation


class GDELTIngestor:

    def __init__(self):

        self.db = EnvironmentalObservationDatabase()

        self.db.initialize()

        self.loader = ObservationLoader()

        self.classifier = EnvironmentalClassifier()

    def _build_observation(self, row):

        try:

            actor = ""
            if pd.notna(row[5]):
                actor = str(row[5])

            location = ""
            if pd.notna(row[53]):
                location = str(row[53])

            tone = None
            if pd.notna(row[30]):
                tone = float(row[30])

            root_code = "00"
            if pd.notna(row[28]):
                root_code = str(row[28]).zfill(2)

            observed = datetime.strptime(
                str(int(row[1])),
                "%Y%m%d"
            )

            return EnvironmentalObservation(

                source="GDELT",

                source_record_id=str(row[0]),

                observation_type=self.classifier.classify_root_code(
                    root_code
                ),

                entity=actor,

                location=location,

                latitude=None,
                longitude=None,

                value=str(row[26]),

                numeric_value=tone,

                unit="tone",

                confidence=0.80,

                observed_at=observed,

                raw_payload=str(row.to_dict())

            )

        except Exception:
            return None

    def ingest(self, zip_path):

        print("Reading GDELT...")

        df = pd.read_csv(
            zip_path,
            sep="\t",
            compression="zip",
            header=None,
            low_memory=False,
        )

        print(f"Loaded {len(df):,} events.")

        self.ingest_dataframe(df)

    def ingest_dataframe(self, df):

        inserted = 0
        failed = 0

        for _, row in df.iterrows():

            observation = self._build_observation(row)

            if observation is None:
                failed += 1
                continue

            try:

                self.loader.insert(observation)

                inserted += 1

            except Exception as e:

                print()

                print("======================================")
                print("FIRST INSERT FAILURE")
                print("======================================")
                print("Exception Type:")
                print(type(e).__name__)
                print()
                print("Exception:")
                print(e)
                print()
                print("Observation:")
                print(observation)
                print("======================================")

                failed += 1

                break
        print()
        print(f"Inserted : {inserted:,}")
        print(f"Failed   : {failed:,}")


if __name__ == "__main__":

    file = Path(
        "data_lake/raw/gdelt/20260630.export.CSV.zip"
    )

    if file.exists():

        GDELTIngestor().ingest(file)

    else:

        print(file)
