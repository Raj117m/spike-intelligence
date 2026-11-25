import duckdb
from datetime import date
import uuid

con = duckdb.connect("data/demand.duckdb")

con.execute("DELETE FROM spikes")

rows = con.execute("""

SELECT

    asin,
    categoryName,
    velocity

FROM candidate_spikes

WHERE velocity >= 5

""").fetchall()

inserted = 0

for asin, category, velocity in rows:

    if velocity >= 20:
        severity = 1.00
    elif velocity >= 10:
        severity = 0.80
    else:
        severity = 0.60

    magnitude = velocity

    acceleration = velocity

    persistence = 1

    con.execute(
        """
        INSERT INTO spikes
        VALUES (?,?,?,?,?,?,?, ?,?)
        """,
        (
            str(uuid.uuid4()),
            asin,
            category,
            date(2023, 9, 1),
            severity,
            magnitude,
            persistence,
            acceleration,
            "ELECOUS_V1",
        ),
    )

    inserted += 1

print(f"Inserted {inserted:,} spikes.")
