from __future__ import annotations

from pathlib import Path
import zipfile

import pandas as pd


class GDELTParser:

    def __init__(self, path):

        self.path = Path(path)

    def load(self):

        with zipfile.ZipFile(self.path) as z:

            filename = z.namelist()[0]

            with z.open(filename) as f:

                df = pd.read_csv(
                    f,
                    sep="\t",
                    header=None,
                    low_memory=False,
                )

        return df
