from demand.graph.builder import EvidenceGraphBuilder
import duckdb

EvidenceGraphBuilder().build()

con = duckdb.connect("data/demand.duckdb")

print(

con.execute("""

SELECT *

FROM evidence_graph

ORDER BY support DESC

LIMIT 20

""").fetchdf()

)
