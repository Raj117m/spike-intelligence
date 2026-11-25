"""
Knowledge Graph persistence layer.

Stores products, factors and categories in DuckDB.
"""

from __future__ import annotations

from datetime import datetime
from ..category.concepts import concept
from ..ontology.mappings import canonicalize
from ..reasoning.graph import expand

def ensure_category(con, category: str, source: str = "wikipedia") -> None:
    exists = con.execute(
        "SELECT 1 FROM categories WHERE category_id = ? LIMIT 1",
        [category],
    ).fetchone()

    if exists:
        return

    con.execute(
        """
        INSERT INTO categories
        (category_id, name, source, created_ts)
        VALUES (?, ?, ?, ?)
        """,
        [category, category, source, datetime.utcnow()],
    )


def link_product(con,
                 product: str,
                 category: str,
                 confidence: float = 1.0,
                 source: str = "wikipedia") -> None:
    ensure_category(con, category, source)

    con.execute(
        """
        INSERT INTO product_categories
        (product_id, category_id, confidence, source)
        VALUES (?, ?, ?, ?)
        """,
        [product, category, confidence, source],
    )


def link_factor(con,
                factor: str,
                category: str,
                confidence: float = 1.0,
                source: str = "wikipedia") -> None:
    ensure_category(con, category, source)

    con.execute(
        """
        INSERT INTO factor_categories
        (factor_id, category_id, confidence, source)
        VALUES (?, ?, ?, ?)
        """,
        [factor, category, confidence, source],
    )
def persist_product_categories(
    con,
    product: str,
    categories: list[str],
    source: str = "wikipedia",
) -> int:
    """
    Persist all categories discovered for a product.

    Categories are:
      1. Normalized
      2. Canonicalized
      3. Expanded through the reasoning graph
      4. Stored only once
    """
    inserted = 0

    normalized = set()

    for category in categories:
        category = concept(category)
        category = canonicalize(category)

        if category:
            normalized.add(category)

    expanded = expand(normalized)

    for category in sorted(expanded):
        ensure_category(con, category, source)

        exists = con.execute(
            """
            SELECT 1
            FROM product_categories
            WHERE product_id = ?
              AND category_id = ?
            LIMIT 1
            """,
            [product, category],
        ).fetchone()

        if exists:
            continue

        con.execute(
            """
            INSERT INTO product_categories
            (product_id, category_id, confidence, source)
            VALUES (?, ?, ?, ?)
            """,
            [product, category, 1.0, source],
        )

        inserted += 1

    return inserted
