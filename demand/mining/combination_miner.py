import duckdb

con = duckdb.connect("data/demand.duckdb")

query = """

WITH grouped AS (

SELECT

observation_id,

STRING_AGG(
factor,
' | '
ORDER BY factor
) AS combo

FROM event_factors

GROUP BY observation_id

)

SELECT

combo,

COUNT(*) AS support

FROM grouped

GROUP BY combo

HAVING COUNT(*) >= 5

ORDER BY support DESC

LIMIT 100

"""

print(con.execute(query).fetchdf())
