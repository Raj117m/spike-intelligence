from demand.reconstruction.evidence import EvidencePackage


class EvidenceBuilder:

    def build(self, row):

        return EvidencePackage(

            asin=row["asin"],

            title=row["title"],

            category=row["categoryName"],

            velocity=float(row["velocity"]),

            wikipedia_topic=None,

            news_query=row["title"],

            weather_region="India",

            economic_region="India",
        )
