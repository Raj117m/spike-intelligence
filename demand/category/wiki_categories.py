"""
Wikipedia category extraction.

Given a Wikipedia page title, return its categories.

This is the foundation for cross-category intelligence.
"""

from __future__ import annotations

import requests


API = "https://en.wikipedia.org/w/api.php"


def categories(title: str) -> list[str]:
    params = {
        "action": "query",
        "titles": title,
        "prop": "categories",
        "cllimit": "max",
        "format": "json",
    }

    r = requests.get(API, params=params, timeout=20)
    r.raise_for_status()

    pages = r.json()["query"]["pages"]

    for page in pages.values():
        cats = page.get("categories", [])
        return [
            c["title"].replace("Category:", "")
            for c in cats
        ]

    return []
