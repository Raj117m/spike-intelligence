import pandas as pd


class FactorExtractor:

    def extract(self, row):

        factors = []

        def add(value):

            if pd.isna(value):
                return

            value = str(value).strip()

            if value == "":
                return

            factors.append(value)

        add(row[5])     # Actor1
        add(row[15])    # Actor2
        add(row[28])    # Root Event
        add(row[29])    # Event Code
        add(row[37])    # Goldstein
        add(row[30])    # Tone
        add(row[31])    # Mentions
        add(row[32])    # Sources
        add(row[33])    # Articles
        add(row[51])    # Country
        add(row[53])    # Location

        return list(set(factors))
