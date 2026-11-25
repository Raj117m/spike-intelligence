import duckdb

from demand.linking.window_builder import WindowBuilder

WindowBuilder().build()

con=duckdb.connect("data/demand.duckdb")

print()

print(

con.execute("""

SELECT COUNT(*)

FROM spike_windows

""").fetchdf()

)

print()

print(

con.execute("""

SELECT *

FROM spike_windows

LIMIT 20

""").fetchdf()

)
