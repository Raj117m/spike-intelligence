"""
Simple category similarity engine.
"""

from __future__ import annotations

from .models import SimilarityResult


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def compare(product_a: str,
            categories_a: list[str],
            product_b: str,
            categories_b: list[str]) -> SimilarityResult:
    score = jaccard(set(categories_a), set(categories_b))

    return SimilarityResult(
        score=score,
        matched_categories=sorted(set(categories_a) & set(categories_b)),
        explanation=(
            f"{product_a} vs {product_b}: "
            f"{len(set(categories_a) & set(categories_b))} shared categories"
        ),
    )
