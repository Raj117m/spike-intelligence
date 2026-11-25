from pathlib import Path
import zipfile
import pandas as pd


class HistoricalParser:

    def parse(self, archive: Path):

        with zipfile.ZipFile(archive) as z:

            name = z.namelist()[0]

            with z.open(name) as f:

                df = pd.read_csv(
                    f,
                    sep="\t",
                    header=None,
                    low_memory=False,
                    dtype=str,
                )

        return df
