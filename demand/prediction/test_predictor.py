from demand.prediction.predictor import Predictor
import duckdb

Predictor().run()

con = duckdb.connect("data/demand.duckdb")

print(

con.execute("""

SELECT

segment,
prob,
window_start,
window_end,
status

FROM predictions

ORDER BY prob DESC

LIMIT 20

""").fetchdf()

)
