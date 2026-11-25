from demand.graph.database import GraphDatabase

db = GraphDatabase()

db.initialize()

print(db.stats())
