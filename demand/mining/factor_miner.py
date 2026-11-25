import duckdb


class FactorMiner:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def discover(self):

        df = self.con.execute("""

        SELECT

            category,

            STRING_AGG(DISTINCT factor, ' + ') AS factors,

            COUNT(*) AS support

        FROM evidence_graph

        GROUP BY category

        HAVING COUNT(*) >= 2

        ORDER BY support DESC

        """).fetchdf()

        return df


if __name__ == "__main__":

    miner = FactorMiner()

    print(miner.discover())
