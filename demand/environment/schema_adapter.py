from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(slots=True)
class CanonicalEvent:

    event_id: str
    date: str

    actor1: str
    actor2: str

    root_code: str
    event_code: str

    tone: Optional[float]
    goldstein: Optional[float]

    mentions: Optional[int]
    sources: Optional[int]
    articles: Optional[int]

    location_name: str
    country: str
    admin1: str

    latitude: Optional[float]
    longitude: Optional[float]

    url: str


class SchemaAdapter:

    def text(self, row, index):

        try:

            value = row[index]

            if pd.isna(value):
                return ""

            return str(value).strip()

        except Exception:

            return ""

    def integer(self, row, index):

        try:

            if pd.isna(row[index]):
                return None

            return int(float(row[index]))

        except Exception:

            return None

    def floating(self, row, index):

        try:

            if pd.isna(row[index]):
                return None

            return float(row[index])

        except Exception:

            return None

    def adapt(self, row) -> CanonicalEvent:

        columns = len(row)

        if columns >= 58:

            return self._modern(row)

        return self._legacy(row)

    def _modern(self, row):

        return CanonicalEvent(

            event_id=self.text(row, 0),

            date=self.text(row, 1),

            actor1=self.text(row, 5),

            actor2=self.text(row, 15),

            root_code=self.text(row, 28),

            event_code=self.text(row, 29),

            tone=self.floating(row, 30),

            goldstein=self.floating(row, 34),

            mentions=self.integer(row, 31),

            sources=self.integer(row, 32),

            articles=self.integer(row, 33),

            location_name=self.text(row, 43),

            country=self.text(row, 44),

            admin1=self.text(row, 48),

            latitude=self.floating(row, 46),

            longitude=self.floating(row, 47),

            url=self.text(row, 57),

        )

    def _legacy(self, row):

        return CanonicalEvent(

            event_id=self.text(row, 0),

            date=self.text(row, 1),

            actor1=self.text(row, 5),

            actor2=self.text(row, 15),

            root_code=self.text(row, 28),

            event_code=self.text(row, 29),

            tone=self.floating(row, 30),

            goldstein=self.floating(row, 34),

            mentions=self.integer(row, 31),

            sources=self.integer(row, 32),

            articles=self.integer(row, 33),

            location_name=self.text(row, 43),

            country=self.text(row, 44),

            admin1=self.text(row, 48),

            latitude=self.floating(row, 46),

            longitude=self.floating(row, 47),

            url="",

        )


if __name__ == "__main__":

    df = pd.read_csv(

        "data_lake/raw/gdelt/20260630.export.CSV.zip",

        sep="\t",

        compression="zip",

        header=None,

        low_memory=False,

        nrows=5,

    )

    adapter = SchemaAdapter()

    for _, row in df.iterrows():

        print(adapter.adapt(row))
