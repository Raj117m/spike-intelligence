from demand.factors.database import FactorDatabase

db = FactorDatabase()

db.create()

print()

print(
    "Rows:",
    db.count(),
)
