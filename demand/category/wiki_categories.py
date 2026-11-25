"""
Wikipedia category extraction.

Uses the MediaWiki API with urllib (no external dependencies).
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"

IGNORED_PREFIXES = (
    "Articles ",
    "All Wikipedia",
    "Wikipedia ",
    "CS1 ",
    "Use ",
    "Pages ",
    "Short description",
    "Webarchive",
    "Template",
    "Redirect",
    "Commons ",
    "Engvar",
    "Harv",
    "Tracking",
    "Coordinates",
    "Good articles",
)

IGNORED_EXACT = {
    "Articles with short description",
    "Articles with excerpts",
}


def categories(title: str) -> list[str]:
    """
    Return cleaned Wikipedia categories for a page.
    """

    params = {
        "action": "query",
        "titles": title,
        "prop": "categories",
        "cllimit": "max",
        "format": "json",
    }

    url = API + "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SpikeIntelligence/1.0"},
    )

    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.load(resp)

    pages = payload.get("query", {}).get("pages", {})

    for page in pages.values():
        clean = []

        for c in page.get("categories", []):
            name = c["title"].replace("Category:", "")

            if name in IGNORED_EXACT:
                continue

            if any(name.startswith(prefix) for prefix in IGNORED_PREFIXES):
                continue

            clean.append(name)

        return clean

    return []
