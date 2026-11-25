from demand.evolution.evolve import SignatureEvolution
import duckdb

SignatureEvolution().evolve()

con = duckdb.connect("data/demand.duckdb")

print(
    con.execute("""
    SELECT
        factor_set,
        hit_rate,
        support_n
    FROM signatures
    ORDER BY hit_rate DESC
    LIMIT 20
    """).fetchdf()
)
