from demand.factors.database import FactorDatabase


class FactorLoader:

    def __init__(self):

        self.db = FactorDatabase()

    def insert(

        self,
        observation_id,
        factor,
        factor_type,
        factor_value,
        observed_at,

    ):

        self.db.con.execute(

            """
            INSERT INTO event_factors
            VALUES(
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,

            (

                observation_id,
                factor,
                factor_type,
                factor_value,
                observed_at,

            )

        )
