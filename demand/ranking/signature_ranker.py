import duckdb


class SignatureRanker:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def rank(self):

        return self.con.execute("""

        SELECT

            factor_set,

            category_scope,

            hit_rate,

            support_n,

            hit_rate * LOG10(support_n + 1) AS score

        FROM signatures

        ORDER BY score DESC, support_n DESC

        """).fetchdf()


if __name__ == "__main__":

    print(SignatureRanker().rank())
