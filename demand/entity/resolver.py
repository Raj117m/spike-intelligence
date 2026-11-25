"""
Entity Resolution Engine v1

Maps Amazon products to external entities.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class EntityMatch:
    asin: str
    product: str
    query: str
    confidence: float


def build_query(title: str, category: str | None = None) -> str:
    """
    Build the first search query that will later be
    sent to Wikipedia / Wikidata.
    """

    query = title.strip()

    if category:
        query += f" {category}"

    return query


def initial_match(
    asin: str,
    title: str,
    category: str | None = None,
) -> EntityMatch:

    return EntityMatch(
        asin=asin,
        product=title,
        query=build_query(title, category),
        confidence=0.0,
    )
