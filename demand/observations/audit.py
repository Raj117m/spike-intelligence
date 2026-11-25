from demand.observations.database import ObservationDatabase

db = ObservationDatabase()

print("\nTOTAL OBSERVATIONS")
print(db.count())

print("\nSAMPLE RECORDS")

print(
    db.con.execute(
        """
        SELECT
            source,
            observation_type,
            entity,
            location,
            value,
            unit,
            observed_at
        FROM observations
        LIMIT 25
        """
    ).fetchdf()
)

print("\nOBSERVATIONS PER SOURCE")

print(
    db.con.execute(
        """
        SELECT
            source,
            COUNT(*) AS observations
        FROM observations
        GROUP BY source
        ORDER BY observations DESC
        """
    ).fetchdf()
)
