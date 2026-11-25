from demand.observations.database import ObservationDatabase

db = ObservationDatabase()

db.initialize()

print()

print("Observation Engine Ready")

print()

print("Current observations:", db.count())
