import duckdb


class Correlator:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def environmental_summary(self):

        return self.con.execute("""

        SELECT

            observation_type,

            COUNT(*) observations,

            COUNT(DISTINCT location) locations,

            AVG(confidence) avg_confidence

        FROM environmental_observations

        GROUP BY observation_type

        ORDER BY observations DESC

        """).fetchdf()

    def spike_summary(self):

        return self.con.execute("""

        SELECT

            COUNT(*) spikes,

            AVG(severity) avg_severity,

            AVG(magnitude) avg_magnitude

        FROM spikes

        """).fetchdf()
