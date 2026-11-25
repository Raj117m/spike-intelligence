from pathlib import Path

from demand.history.history_loader import HistoryLoader


loader = HistoryLoader()

root = Path("data_lake/raw/gdelt_history")

files = sorted(root.glob("*.zip"))

print()

print("Archives :", len(files))

print()

for file in files:

    loader.ingest_archive(file)
