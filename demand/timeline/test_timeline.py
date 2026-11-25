from demand.timeline.correlator import TimelineCorrelator

t = TimelineCorrelator()

print()

print("OBSERVATIONS")

print(t.observation_counts())

print()

print("SPIKES")

print(t.spike_counts())
