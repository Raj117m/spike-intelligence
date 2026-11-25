from __future__ import annotations

from demand.world.event import WorldEvent


class EventNormalizer:

    def convert(self, row):

        return WorldEvent(

            id=int(row["GLOBALEVENTID"]),

            date=int(row["SQLDATE"]),

            actor1=row["Actor1Name"],

            actor2=row["Actor2Name"],

            event_code=str(row["EventCode"]),

            mentions=int(row["NumMentions"]),

            tone=float(row["AvgTone"]),

            location=row["ActionGeo_FullName"],

            source_url=row["SOURCEURL"],

        )
