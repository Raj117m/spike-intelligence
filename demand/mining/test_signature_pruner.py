import duckdb

from demand.mining.signature_pruner import SignaturePruner

SignaturePruner().prune()

con=duckdb.connect("data/demand.duckdb")

print()

print(

con.execute("""

SELECT COUNT(*)

FROM signature_library

""").fetchdf()

)

print()

print(

con.execute("""

SELECT *

FROM signature_library

ORDER BY final_score DESC

LIMIT 50

""").fetchdf()

)
