import duckdb

from demand.mining.quad_miner import QuadMiner

QuadMiner().build()

con = duckdb.connect("data/demand.duckdb")

print()

print(
con.execute("""

SELECT COUNT(*)

FROM factor_quads

""").fetchdf()
)

print()

print(
con.execute("""

SELECT *

FROM factor_quads

ORDER BY support DESC

LIMIT 50

""").fetchdf()
)
