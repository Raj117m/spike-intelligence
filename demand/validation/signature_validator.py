import duckdb


class SignatureValidator:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def validate(self):

        self.con.execute("""

        UPDATE signatures s

        SET

            support_n = (

                SELECT COUNT(*)

                FROM evidence_graph e

                WHERE
                    e.factor || '|' || e.mechanism = s.factor_set
                    AND e.category = s.category_scope

            ),

            hit_rate = (

                SELECT

                    CASE

                        WHEN COUNT(*)=0 THEN 0

                        ELSE AVG(confidence)

                    END

                FROM evidence_graph e

                WHERE
                    e.factor || '|' || e.mechanism = s.factor_set
                    AND e.category = s.category_scope

            )

        """)

        print("Signatures revalidated.")


if __name__ == "__main__":

    SignatureValidator().validate()
