"""
Experiment E001

Measure latent attention from Wikipedia.
"""

from demand.scientist.wikipedia import WikipediaSensor
from demand.scientist.attention import (
    estimate_attention,
    peak_attention,
    growth,
)

TOPIC = "2026_FIFA_World_Cup"


def run():

    sensor = WikipediaSensor()

    rows = sensor.pageviews(TOPIC)

    print("\n=== Experiment E001 ===")
    print(f"Topic: {TOPIC}")
    print(f"Observations: {len(rows)}")
    print(f"Mean Attention: {estimate_attention(rows):.2f}")
    print(f"Peak Attention: {peak_attention(rows):.2f}")
    print(f"Growth: {growth(rows):.4f}")


if __name__ == "__main__":
    run()
