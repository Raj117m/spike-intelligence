"""
Wikipedia-backed classifier.

Uses real Wikipedia categories instead of keyword rules.
"""

from __future__ import annotations

from .models import ClassificationResult
from .wiki_categories import categories


def classify(product: str) -> ClassificationResult:
    try:
        cats = categories(product)
    except Exception as exc:
        return ClassificationResult(
            product=product,
            primary_category="Unknown",
            confidence=0.0,
            reason=str(exc),
        )

    if not cats:
        return ClassificationResult(
            product=product,
            primary_category="Unknown",
            confidence=0.0,
            reason="No Wikipedia categories",
        )

    return ClassificationResult(
        product=product,
        primary_category=cats[0],
        secondary_categories=cats[1:],
        confidence=1.0,
        reason="Wikipedia category extraction",
    )
