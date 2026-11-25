"""
Concept relationship graph and reasoning utilities.
"""

from __future__ import annotations

GRAPH = {
    "Conversational AI": {
        "Generative AI",
    },

    "Generative AI": {
        "Artificial Intelligence",
        "Software",
    },

    "Artificial Intelligence": {
        "Technology",
    },

    "Software": {
        "Technology",
        "Consumer Software",
    },

    "Consumer Software": {
        "Consumer",
    },

    "Productivity Software": {
        "Consumer Software",
        "Software",
    },

    "Sports": {
        "Entertainment",
    },

    "Entertainment": {
        "Consumer",
    },

    "Retail": {
        "Consumer",
    },
}


def parents(concept: str) -> set[str]:
    return GRAPH.get(concept, set())


def expand(concepts: set[str]) -> set[str]:
    """
    Expand a set of concepts by recursively following parent relationships.
    """

    result = set(concepts)

    queue = list(concepts)

    while queue:
        current = queue.pop()

        for parent in GRAPH.get(current, set()):
            if parent not in result:
                result.add(parent)
                queue.append(parent)

    return result
