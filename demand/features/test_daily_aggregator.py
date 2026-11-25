import duckdb

from demand.features.daily_aggregator import DailyAggregator

DailyAggregator().build()

con = duckdb.connect(
    "data/demand.duckdb"
)

print()

print(

con.execute("""

SELECT COUNT(*)

FROM daily_feature_store

""").fetchdf()

)

print()

print(

con.execute("""

SELECT *

FROM daily_feature_store

LIMIT 20

""").fetchdf()

)
