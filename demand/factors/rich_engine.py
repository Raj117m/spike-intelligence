from __future__ import annotations

from dataclasses import dataclass

from demand.environment.schema_adapter import (
    CanonicalEvent,
)


@dataclass(slots=True)
class Factor:

    factor_type: str
    factor_value: object
    weight: float = 1.0


class RichFactorEngine:

    ROOT_TYPES = {

        "01": "STATEMENT",
        "02": "APPEAL",
        "03": "COOPERATION",
        "04": "CONSULT",
        "05": "DIPLOMACY",
        "06": "AID",
        "07": "SUPPORT",
        "08": "AGREEMENT",
        "09": "INVESTIGATION",
        "10": "DEMAND",
        "11": "DISAPPROVAL",
        "12": "REJECT",
        "13": "THREAT",
        "14": "PROTEST",
        "15": "FORCE",
        "16": "VIOLENCE",
        "17": "COERCION",
        "18": "ASSAULT",
        "19": "FIGHT",
        "20": "WAR",

    }

    def __init__(self):

        self.factors = []

    def add(
        self,
        factor_type,
        value,
        weight=1.0,
    ):

        if value is None:
            return

        if str(value).strip() == "":
            return

        self.factors.append(
            Factor(
                factor_type,
                value,
                weight,
            )
        )

    def extract(
        self,
        event: CanonicalEvent,
    ):

        self.factors = []

        self.actor_features(event)

        self.event_features(event)

        self.location_features(event)

        self.sentiment_features(event)

        self.media_features(event)

        self.time_features(event)

        return self.normalize()

    def actor_features(self, event):

        self.add("ACTOR1", event.actor1)

        self.add("ACTOR2", event.actor2)

    def event_features(self, event):

        self.add(
            "ROOT_CODE",
            event.root_code,
            2.0,
        )

        self.add(
            "EVENT_CODE",
            event.event_code,
            1.5,
        )

        if event.root_code in self.ROOT_TYPES:

            self.add(

                "ROOT_EVENT",

                self.ROOT_TYPES[event.root_code],

                3.0,

            )

        if event.goldstein is not None:

            self.add(

                "GOLDSTEIN",

                round(event.goldstein, 2),

                2.0,

            )

    def location_features(self, event):

        self.add(
            "COUNTRY",
            event.country,
            2.5,
        )

        self.add(
            "STATE",
            event.admin1,
            1.5,
        )

        self.add(
            "LOCATION",
            event.location_name,
            2.0,
        )

        if event.latitude is not None:

            self.add(
                "LATITUDE",
                round(event.latitude, 2),
            )

        if event.longitude is not None:

            self.add(
                "LONGITUDE",
                round(event.longitude, 2),
            )

    def sentiment_features(self, event):

        if event.tone is None:
            return

        self.add(
            "RAW_TONE",
            round(event.tone, 2),
        )

        if event.tone <= -10:

            label = "EXTREME_NEGATIVE"

        elif event.tone <= -5:

            label = "VERY_NEGATIVE"

        elif event.tone < 0:

            label = "NEGATIVE"

        elif event.tone == 0:

            label = "NEUTRAL"

        elif event.tone < 5:

            label = "POSITIVE"

        else:

            label = "VERY_POSITIVE"

        self.add(
            "TONE",
            label,
            2.0,
        )

    def media_features(self, event):

        self.add(
            "MENTIONS",
            event.mentions,
        )

        self.add(
            "SOURCES",
            event.sources,
        )

        self.add(
            "ARTICLES",
            event.articles,
        )

    def time_features(self, event):

        if len(event.date) >= 6:

            self.add(
                "YEAR",
                event.date[:4],
            )

            self.add(
                "MONTH",
                event.date[4:6],
            )

    def normalize(self):

        output = []

        seen = set()

        for factor in self.factors:

            key = (
                factor.factor_type,
                str(factor.factor_value),
            )

            if key in seen:
                continue

            seen.add(key)

            output.append(factor)

        return output


if __name__ == "__main__":

    from pathlib import Path

    import pandas as pd

    from demand.environment.schema_adapter import (
        SchemaAdapter,
    )

    df = pd.read_csv(

        Path(
            "data_lake/raw/gdelt/20260630.export.CSV.zip"
        ),

        sep="\t",

        compression="zip",

        header=None,

        low_memory=False,

        nrows=5,

    )

    adapter = SchemaAdapter()

    engine = RichFactorEngine()

    event = adapter.adapt(df.iloc[0])

    factors = engine.extract(event)

    print()

    print("Factors:", len(factors))

    print()

    for factor in factors:

        print(factor)
