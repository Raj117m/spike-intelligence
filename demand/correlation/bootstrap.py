from demand.correlation.database import CorrelationDatabase

db = CorrelationDatabase()

db.initialize()

print(db.stats())
