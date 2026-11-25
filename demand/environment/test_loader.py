from datetime import datetime

from demand.environment.loader import ObservationLoader
from demand.environment.models import EnvironmentalObservation

loader = ObservationLoader()

obs = EnvironmentalObservation(
    source="TEST",
    source_record_id="1",
    observation_type="Rainfall",
    entity="Mumbai",
    location="Mumbai",
    latitude=19.076,
    longitude=72.8777,
    value="180",
    numeric_value=180.0,
    unit="mm",
    confidence=0.95,
    observed_at=datetime.now(),
    raw_payload="manual test"
)

loader.insert(obs)

print("Inserted successfully.")
