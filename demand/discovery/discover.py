"""
Automatic factor discovery.

This module proposes candidate environmental factors
that may explain a product's demand.
"""

from __future__ import annotations


def discover(product: str, related_topics: list[str]) -> list[str]:
    """
    Return candidate causal factors.

    For now this simply returns the related topics.
    Later this will merge information from:
        - Wikipedia
        - News
        - Google Trends
        - Reddit
        - Amazon
        - Weather
        - Events
    """

    seen = set()
    factors = []

    for topic in related_topics:
        if topic in seen:
            continue

        seen.add(topic)
        factors.append(topic)

    return factors
