from demand.discovery.windowed_lead_engine import WindowedLeadEngine

engine = WindowedLeadEngine()

df = engine.build(60)

print(df.head(100))

print()

print("Relationships:", len(df))
