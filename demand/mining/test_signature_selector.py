import duckdb

from demand.mining.signature_selector import SignatureSelector

SignatureSelector().build()

con = duckdb.connect("data/demand.duckdb")

print()

print(

con.execute("""

SELECT COUNT(*)

FROM production_signatures

""").fetchdf()

)

print()

print(

con.execute("""

SELECT *

FROM production_signatures

ORDER BY prediction_score DESC

LIMIT 50

""").fetchdf()

)
