"""
Concept extraction from noisy Wikipedia categories.
"""

from __future__ import annotations

import re

STOP_WORDS = {
    "articles",
    "article",
    "wikipedia",
    "pages",
    "page",
    "templates",
    "template",
    "redirects",
    "redirect",
    "use",
    "cs1",
    "engvar",
    "tracking",
    "coordinates",
    "good",
    "featured",
    "all",
    "written",
    "american",
    "british",
    "english",
    "language",
    "sources",
    "source",
    "winner",
    "winners",
    "award",
    "awards",
}


def concept(category: str) -> str:
    """
    Convert a Wikipedia category into a reusable concept.
    """

    text = category.lower()

    # remove years
    text = re.sub(r"\b(19|20)\d{2}\b", "", text)

    # remove punctuation
    text = re.sub(r"[^a-z0-9 ]", " ", text)

    words = []

    for word in text.split():
        if word in STOP_WORDS:
            continue

        words.append(word)

    return " ".join(words).strip().title()
