"""
Entity Resolution Engine v2

Maps Amazon products to clean search entities that can later be
linked to Wikipedia, News, Google Trends and other public data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class ResolvedEntity:

    asin: str
    title: str
    brand: str | None
    entity: str
    search_query: str
    category: str


class EntityResolver:

    BRAND_PATTERN = re.compile(r"^[A-Za-z0-9&+\-]+")

    def resolve(
        self,
        asin: str,
        title: str,
        category: str,
    ) -> ResolvedEntity:

        title = " ".join(title.split())

        m = self.BRAND_PATTERN.match(title)

        brand = m.group(0) if m else None

        entity = title

        if brand:

            entity = title.replace(brand, "", 1).strip()

        query = f"{title} {category}"

        return ResolvedEntity(
            asin=asin,
            title=title,
            brand=brand,
            entity=entity,
            search_query=query,
            category=category,
        )
