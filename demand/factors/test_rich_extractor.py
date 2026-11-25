import pandas as pd

from demand.factors.rich_extractor import RichFactorExtractor

df = pd.read_csv(
    "data_lake/raw/gdelt/20260630.export.CSV.zip",
    sep="\t",
    compression="zip",
    header=None,
    low_memory=False,
)

extractor = RichFactorExtractor()

factors = extractor.extract(df.iloc[0])

print()

print("Factor Count:", len(factors))

print()

for factor in factors:
    print(factor)
