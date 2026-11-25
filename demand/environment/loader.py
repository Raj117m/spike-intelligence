from demand.environment.database import EnvironmentalObservationDatabase


class ObservationLoader:

    def __init__(self):
        self.db = EnvironmentalObservationDatabase()

    def insert(self, observation):

        self.db.con.execute(
            """
            INSERT INTO environmental_observations(

                source,
                source_record_id,
                observation_type,
                entity,
                location,
                latitude,
                longitude,
                value,
                numeric_value,
                unit,
                confidence,
                observed_at,
                raw_payload

            )

            VALUES (

                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?

            )
            """,
            (

                observation.source,
                observation.source_record_id,
                observation.observation_type,
                observation.entity,
                observation.location,
                observation.latitude,
                observation.longitude,
                observation.value,
                observation.numeric_value,
                observation.unit,
                observation.confidence,
                observation.observed_at,
                observation.raw_payload,

            ),
        )
