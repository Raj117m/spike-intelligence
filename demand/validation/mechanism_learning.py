import duckdb


class MechanismLearning:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def initialize(self):

        self.con.execute("""

        CREATE TABLE IF NOT EXISTS mechanism_learning(

            mechanism VARCHAR PRIMARY KEY,

            successes INTEGER DEFAULT 0,

            failures INTEGER DEFAULT 0,

            confidence DOUBLE DEFAULT 0.50,

            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

    def update(self, mechanism, success):

        row = self.con.execute(

            """

            SELECT successes, failures

            FROM mechanism_learning

            WHERE mechanism=?

            """,

            (mechanism,),

        ).fetchone()

        if row is None:

            s = 1 if success else 0

            f = 0 if success else 1

        else:

            s, f = row

            if success:

                s += 1

            else:

                f += 1

        confidence = s / max(1, s + f)

        self.con.execute(

            """

            DELETE FROM mechanism_learning

            WHERE mechanism=?

            """,

            (mechanism,),

        )

        self.con.execute(

            """

            INSERT INTO mechanism_learning

            VALUES(

                ?,?,?,?,
                CURRENT_TIMESTAMP

            )

            """,

            (

                mechanism,

                s,

                f,

                confidence,

            ),

        )

    def report(self):

        return self.con.execute(

            """

            SELECT *

            FROM mechanism_learning

            ORDER BY confidence DESC

            """

        ).fetchdf()
