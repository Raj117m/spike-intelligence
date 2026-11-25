import pandas as pd


class RichFactorExtractor:

    def extract(self, row):

        factors = []

        def add(name, value):

            if pd.isna(value):
                return

            value = str(value).strip()

            if value == "":
                return

            factors.append(
                {
                    "type": name,
                    "value": value
                }
            )

        # ---------------------
        # Actors
        # ---------------------

        add("ACTOR1", row[5])
        add("ACTOR2", row[15])

        # ---------------------
        # Event Codes
        # ---------------------

        add("ROOT_CODE", row[28])
        add("EVENT_CODE", row[29])

        # ---------------------
        # Geography
        # ---------------------

        add("COUNTRY", row[51])
        add("LOCATION", row[53])

        # ---------------------
        # Tone
        # ---------------------

        if pd.notna(row[30]):

            tone = float(row[30])

            if tone >= 5:
                add("TONE", "VERY_POSITIVE")
            elif tone >= 1:
                add("TONE", "POSITIVE")
            elif tone <= -5:
                add("TONE", "VERY_NEGATIVE")
            elif tone < 0:
                add("TONE", "NEGATIVE")
            else:
                add("TONE", "NEUTRAL")

            add("RAW_TONE", tone)

        # ---------------------
        # Goldstein
        # ---------------------

        if pd.notna(row[37]):

            score = float(row[37])

            if score >= 5:
                add("GOLDSTEIN", "VERY_POSITIVE")
            elif score >= 1:
                add("GOLDSTEIN", "POSITIVE")
            elif score <= -5:
                add("GOLDSTEIN", "VERY_NEGATIVE")
            elif score < 0:
                add("GOLDSTEIN", "NEGATIVE")
            else:
                add("GOLDSTEIN", "NEUTRAL")

            add("RAW_GOLDSTEIN", score)

        # ---------------------
        # Mentions
        # ---------------------

        if pd.notna(row[31]):

            mentions = int(row[31])

            if mentions > 500:

                add("MENTIONS", "EXTREME")

            elif mentions > 100:

                add("MENTIONS", "HIGH")

            elif mentions > 20:

                add("MENTIONS", "MEDIUM")

            else:

                add("MENTIONS", "LOW")

        # ---------------------
        # Sources
        # ---------------------

        if pd.notna(row[32]):

            sources = int(row[32])

            if sources > 100:

                add("SOURCES", "VERY_HIGH")

            elif sources > 20:

                add("SOURCES", "HIGH")

            else:

                add("SOURCES", "LOW")

        # ---------------------
        # Articles
        # ---------------------

        if pd.notna(row[33]):

            articles = int(row[33])

            if articles > 100:

                add("ARTICLES", "VERY_HIGH")

            elif articles > 20:

                add("ARTICLES", "HIGH")

            else:

                add("ARTICLES", "LOW")

        return factors
