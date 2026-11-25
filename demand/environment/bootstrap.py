from demand.environment.database import EnvironmentalObservationDatabase

db = EnvironmentalObservationDatabase()

db.initialize()

print()

print("ENVIRONMENTAL OBSERVATION WAREHOUSE")

print()

print(db.stats())
