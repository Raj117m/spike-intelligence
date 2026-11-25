import pandas as pd

from demand.environment.schema_adapter import SchemaAdapter

df = pd.read_csv(
    "data_lake/raw/gdelt/20260630.export.CSV.zip",
    sep="\t",
    compression="zip",
    header=None,
    low_memory=False,
    nrows=5
)

adapter = SchemaAdapter()

for _, row in df.iterrows():

    event = adapter.adapt(row)

    print(event)

    print("-"*80)
