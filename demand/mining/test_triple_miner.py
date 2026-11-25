import duckdb

from demand.mining.triple_miner import TripleMiner

TripleMiner().build()

con = duckdb.connect("data/demand.duckdb")

print()

print(
con.execute("""

SELECT COUNT(*)

FROM factor_triples

""").fetchdf()
)

print()

print(
con.execute("""

SELECT *

FROM factor_triples

ORDER BY support DESC

LIMIT 50

""").fetchdf()
)
