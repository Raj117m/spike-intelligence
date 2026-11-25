"""
Wikidata provider.

Uses the official Wikidata search API.
"""

from __future__ import annotations

import requests

from demand.providers.base import Provider, ProviderResult


class WikidataProvider(Provider):

    URL = "https://www.wikidata.org/w/api.php"

    def search(self, query: str):

        r = requests.get(
            self.URL,
            params={
                "action": "wbsearchentities",
                "language": "en",
                "format": "json",
                "search": query,
            },
            timeout=30,
        )

        r.raise_for_status()

        data = r.json()

        results = []

        for item in data.get("search", []):

            results.append(

                ProviderResult(

                    source="wikidata",

                    query=query,

                    confidence=float(item.get("match", {}).get("score", 0.0)),

                    data=item,
                )

            )

        return results
