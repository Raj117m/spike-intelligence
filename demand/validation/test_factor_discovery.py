from datetime import datetime

from demand.environment.models import EnvironmentalObservation
from demand.validation.factor_discovery import FactorDiscovery

obs = [

    EnvironmentalObservation(

        source="IMD",

        source_record_id="1",

        observation_type="Rainfall",

        entity="Mumbai",

        location="Mumbai",

        latitude=None,

        longitude=None,

        value="245",

        numeric_value=245,

        unit="mm",

        confidence=0.95,

        observed_at=datetime.now(),

        raw_payload="",

    ),

    EnvironmentalObservation(

        source="CPCB",

        source_record_id="2",

        observation_type="AQI",

        entity="Delhi",

        location="Delhi",

        latitude=None,

        longitude=None,

        value="310",

        numeric_value=310,

        unit="AQI",

        confidence=0.90,

        observed_at=datetime.now(),

        raw_payload="",

    ),

]

engine = FactorDiscovery()

print(

    engine.discover(

        mechanism="FLOOD_SUPPLY_CHAIN",

        observations=obs,

        prediction_correct=False,

    )

)
