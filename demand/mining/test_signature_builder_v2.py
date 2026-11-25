import duckdb

from demand.mining.signature_builder_v2 import SignatureBuilder

SignatureBuilder().build()

con=duckdb.connect("data/demand.duckdb")

print()

print(

con.execute("""

SELECT COUNT(*)

FROM learned_signatures

""").fetchdf()

)

print()

print(

con.execute("""

SELECT *

FROM learned_signatures

ORDER BY score DESC

LIMIT 50

""").fetchdf()

)
