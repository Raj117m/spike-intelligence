import duckdb

con = duckdb.connect("data/demand.duckdb")

print()

print("TOTAL")

print(
    con.execute(
        "SELECT COUNT(*) FROM candidate_spikes"
    ).fetchdf()
)

print()

print("TOP 20")

print(
    con.execute(
        """
        SELECT *

        FROM candidate_spikes

        ORDER BY velocity DESC

        LIMIT 20
        """
    ).fetchdf()
)

print()

print("VELOCITY DISTRIBUTION")

print(
    con.execute(
        """
        SELECT

            MIN(velocity),

            AVG(velocity),

            MAX(velocity)

        FROM candidate_spikes
        """
    ).fetchdf()
)
