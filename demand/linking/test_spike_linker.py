import duckdb

from demand.linking.spike_linker import SpikeLinker

SpikeLinker().build()

con=duckdb.connect("data/demand.duckdb")

print()

print(

con.execute("""

SELECT COUNT(*)

FROM spike_factor_links

""").fetchdf()

)

print()

print(

con.execute("""

SELECT *

FROM spike_factor_links

LIMIT 50

""").fetchdf()

)
