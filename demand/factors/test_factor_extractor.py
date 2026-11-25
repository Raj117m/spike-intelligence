import pandas as pd

from demand.factors.extractor import FactorExtractor

df = pd.read_csv(
    "data_lake/raw/gdelt/20260630.export.CSV.zip",
    sep="\t",
    compression="zip",
    header=None,
    low_memory=False,
)

extractor = FactorExtractor()

print(extractor.extract(df.iloc[0]))
