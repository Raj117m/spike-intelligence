"""
Canonical ontology used throughout the demand intelligence system.

Everything eventually maps into one of these concepts instead of
storing arbitrary Wikipedia category names.
"""

from __future__ import annotations

CANONICAL = {
    "Artificial Intelligence",
    "Generative AI",
    "Conversational AI",
    "Machine Learning",
    "Software",
    "Consumer Software",
    "Productivity Software",
    "Education",
    "Gaming",
    "Finance",
    "Healthcare",
    "Sports",
    "Entertainment",
    "Travel",
    "Food",
    "Retail",
    "Automotive",
    "Beauty",
    "Fashion",
    "Electronics",
}


def is_canonical(name: str) -> bool:
    return name in CANONICAL


def all_concepts() -> list[str]:
    return sorted(CANONICAL)
