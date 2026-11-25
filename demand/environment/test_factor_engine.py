from datetime import datetime

from demand.environment.factor_engine import FactorEngine
from demand.environment.models import EnvironmentalObservation

engine = FactorEngine()

examples = [

    EnvironmentalObservation(

        source="IMD",

        source_record_id="1",

        observation_type="Rainfall",

        entity="Mumbai",

        location="Mumbai",

        latitude=None,

        longitude=None,

        value="210",

        numeric_value=210,

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

        value="325",

        numeric_value=325,

        unit="AQI",

        confidence=0.99,

        observed_at=datetime.now(),

        raw_payload="",

    ),

    EnvironmentalObservation(

        source="Agmarknet",

        source_record_id="3",

        observation_type="Tomato Price",

        entity="Tomato",

        location="Nashik",

        latitude=None,

        longitude=None,

        value="18",

        numeric_value=18,

        unit="INR",

        confidence=1.0,

        observed_at=datetime.now(),

        raw_payload="",

    ),

]

for obs in examples:

    print()

    print(obs.observation_type)

    print(engine.analyze(obs))
