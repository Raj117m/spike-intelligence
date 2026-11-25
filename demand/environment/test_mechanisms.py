from datetime import datetime

from demand.environment.factor_engine import FactorEngine
from demand.environment.mechanism_engine import MechanismEngine
from demand.environment.models import EnvironmentalObservation

obs = EnvironmentalObservation(

    source="IMD",

    source_record_id="1",

    observation_type="Rainfall",

    entity="Mumbai",

    location="Mumbai",

    latitude=None,

    longitude=None,

    value="240",

    numeric_value=240,

    unit="mm",

    confidence=0.95,

    observed_at=datetime.now(),

    raw_payload="",

)

factor_engine = FactorEngine()

mechanism_engine = MechanismEngine()

factors = factor_engine.analyze(obs)

print()

print("FACTORS")

print(factors)

print()

print("MECHANISMS")

print(mechanism_engine.infer(factors))
