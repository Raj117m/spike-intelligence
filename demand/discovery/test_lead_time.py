from demand.discovery.lead_time_engine import LeadTimeEngine

engine = LeadTimeEngine()

df = engine.build()

print(df.head(100))

print()

print("Relationships:", len(df))
