from datetime import datetime

from demand.mechanisms.evidence import Evidence
from demand.mechanisms.evidence_database import EvidenceDatabase

db = EvidenceDatabase()

db.initialize()

db.save(

Evidence(

    mechanism_id="M0001",

    source="GDELT",

    dataset="20260630.export.CSV.zip",

    entity="Storm",

    observation="Global event observation",

    observed_at=datetime.utcnow(),

    confidence=0.60,

    url=None,

)

)

print(db.all())
