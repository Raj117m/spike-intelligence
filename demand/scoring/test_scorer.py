from demand.scoring.evidence_scorer import EvidenceScorer

import duckdb

EvidenceScorer().score()

con = duckdb.connect("data/demand.duckdb")

print(

con.execute("""

SELECT

factor,

support,

confidence,

precision

FROM evidence_graph

ORDER BY confidence DESC

LIMIT 20

""").fetchdf()

)
