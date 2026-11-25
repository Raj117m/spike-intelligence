import duckdb


class MechanismBuilder:

    def __init__(self):
        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        self.con.execute("""
        UPDATE evidence_graph
        SET mechanism =
        CASE

            WHEN factor='POLITICAL'
                THEN 'POLITICAL_DISRUPTION'

            WHEN factor='CONFLICT'
                THEN 'SUPPLY_CHAIN'

            WHEN factor='SECURITY'
                THEN 'RISK_EVENT'

            WHEN factor='ECONOMY'
                THEN 'ECONOMIC_PRESSURE'

            WHEN factor='SOCIAL'
                THEN 'SOCIAL_TREND'

            WHEN factor='MEDIA'
                THEN 'MEDIA_ATTENTION'

            WHEN factor='LEGAL'
                THEN 'REGULATORY_CHANGE'

            WHEN factor='HUMANITARIAN'
                THEN 'PUBLIC_RESPONSE'

            ELSE 'UNKNOWN'

        END
        """)


if __name__ == "__main__":

    MechanismBuilder().build()

    print("Mechanisms updated.")
