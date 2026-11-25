"""
Provider execution engine.

Handles caching, retries and provenance for all providers.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("data/provider_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class ProviderEngine:

    def __init__(self, provider):
        self.provider = provider

    def search(self, query: str):

        key = hashlib.sha256(query.encode()).hexdigest()

        cache = CACHE_DIR / f"{self.provider.__class__.__name__}_{key}.json"

        if cache.exists():

            with open(cache) as f:
                return json.load(f)

        results = self.provider.search(query)

        serializable = [
            {
                "source": r.source,
                "query": r.query,
                "confidence": r.confidence,
                "data": r.data,
            }
            for r in results
        ]

        with open(cache, "w") as f:
            json.dump(serializable, f, indent=2)

        return serializable
