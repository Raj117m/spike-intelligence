from demand.mechanisms.database import MechanismDatabase
from demand.mechanisms.mechanism import Mechanism

db = MechanismDatabase()

db.initialize()

db.save(

Mechanism(

    id="M0001",

    name="Power Outage Demand",

    description="Electrical outages increase portable energy demand.",

    trigger="Storm",

    latent_state="Power Outage Risk",

    capability="Portable Electricity",

    outcome="Generator Purchases",

    confidence=0.10,

)

)

print(db.all())
