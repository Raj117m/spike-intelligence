from demand.parsers.gdelt import GDELTParser
from demand.parsers.gdelt_schema import COLUMNS
from demand.world.normalizer import EventNormalizer

parser = GDELTParser(
    "data_lake/raw/gdelt/20260630.export.CSV.zip"
)

df = parser.load()

df.columns = [COLUMNS[i] for i in range(len(df.columns))]

normalizer = EventNormalizer()

for _, row in df.head(10).iterrows():

    print()

    print(normalizer.convert(row))
