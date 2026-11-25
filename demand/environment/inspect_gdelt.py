import pandas as pd

df = pd.read_csv(
    "data_lake/raw/gdelt/20260630.export.CSV.zip",
    sep="\t",
    compression="zip",
    header=None,
    low_memory=False,
)

print("Rows:", len(df))
print("Columns:", len(df.columns))

cols = [
    0,   # GLOBALEVENTID
    5,   # Actor1Name
    6,   # Actor1CountryCode
    15,  # Actor2Name
    16,  # Actor2CountryCode
    26,  # EventCode
    27,  # EventBaseCode
    28,  # EventRootCode
    29,  # QuadClass
    30,  # GoldsteinScale
    31,  # NumMentions
    32,  # NumSources
    33,  # NumArticles
    34,  # AvgTone
    53,  # ActionGeo_FullName
]

print(df[cols].head(30))
