"""
Experiment E002

Wikipedia Attention vs Amazon Demand
"""

import duckdb

from demand.scientist.wikipedia import WikipediaSensor
from demand.scientist.attention import estimate_attention

TOPIC = "2026_FIFA_World_Cup"

con = duckdb.connect("data/demand.duckdb")

sensor = WikipediaSensor()

wiki = sensor.pageviews(TOPIC)

attention = estimate_attention(wiki)

print("\nWikipedia")

print("Days:", len(wiki))

print("Average Attention:", round(attention,2))

print()

print("Amazon Products")

print(
    con.execute(
        """
        SELECT COUNT(*)
        FROM amazon_products
        """
    ).fetchone()[0]
)

print()

print("Spikes")

print(
    con.execute(
        """
        SELECT COUNT(*)
        FROM spikes
        """
    ).fetchone()[0]
)
