import duckdb

con = duckdb.connect("data/demand.duckdb")

con.execute("""
DELETE FROM event_factors
""")

con.execute("""
INSERT INTO event_factors

SELECT

source_record_id,

'OBSERVATION_TYPE',

observation_type,

observation_type,

observed_at

FROM environmental_observations
""")

con.execute("""
INSERT INTO event_factors

SELECT

source_record_id,

'ENTITY',

entity,

entity,

observed_at

FROM environmental_observations

WHERE entity IS NOT NULL
AND TRIM(entity) <> ''
""")

con.execute("""
INSERT INTO event_factors

SELECT

source_record_id,

'LOCATION',

location,

location,

observed_at

FROM environmental_observations

WHERE location IS NOT NULL
AND TRIM(location) <> ''
""")

con.execute("""
INSERT INTO event_factors

SELECT

source_record_id,

'TONE',

CASE

WHEN numeric_value >= 5 THEN 'VERY_POSITIVE'

WHEN numeric_value >= 1 THEN 'POSITIVE'

WHEN numeric_value <= -5 THEN 'VERY_NEGATIVE'

WHEN numeric_value < 0 THEN 'NEGATIVE'

ELSE 'NEUTRAL'

END,

CAST(numeric_value AS VARCHAR),

observed_at

FROM environmental_observations

WHERE numeric_value IS NOT NULL
""")

print()

print(
con.execute("""
SELECT COUNT(*)
FROM event_factors
""").fetchdf()
)

print()

print(
con.execute("""
SELECT
factor_type,
COUNT(*)
FROM event_factors
GROUP BY factor_type
ORDER BY COUNT(*) DESC
""").fetchdf()
)
