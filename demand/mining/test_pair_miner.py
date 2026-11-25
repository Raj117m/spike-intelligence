import duckdb

from demand.mining.pair_miner import PairMiner

PairMiner().build()

con = duckdb.connect("data/demand.duckdb")

print()

print(

con.execute("""

SELECT COUNT(*)

FROM factor_pairs

""").fetchdf()

)

print()

print(

con.execute("""

SELECT *

FROM factor_pairs

ORDER BY support DESC

LIMIT 50

""").fetchdf()

)
