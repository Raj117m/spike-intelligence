from demand.validation.database import ValidationDatabase

db = ValidationDatabase()

db.initialize()

print()

print("VALIDATION ENGINE READY")

print()

print(db.stats())
