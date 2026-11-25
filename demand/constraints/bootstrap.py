from demand.constraints.constraint import Constraint
from demand.constraints.database import ConstraintDatabase

db = ConstraintDatabase()

db.initialize()

constraints = [

Constraint(
id="C0001",
name="Electrical Supply Constraint",
category="Infrastructure",
description="Electrical energy cannot reach consumers.",
physical_domain="Energy",
confidence=0.9,
),

Constraint(
id="C0002",
name="Thermal Stress",
category="Climate",
description="Ambient temperature exceeds comfort limits.",
physical_domain="Heat",
confidence=0.9,
),

Constraint(
id="C0003",
name="Water Scarcity",
category="Environment",
description="Available water below required level.",
physical_domain="Water",
confidence=0.9,
),

Constraint(
id="C0004",
name="Mobility Constraint",
category="Transportation",
description="Movement through space is restricted.",
physical_domain="Transport",
confidence=0.9,
),

Constraint(
id="C0005",
name="Financial Constraint",
category="Economics",
description="Available purchasing power is insufficient.",
physical_domain="Economy",
confidence=0.9,
)

]

for c in constraints:

    db.save(c)

print(db.all())
