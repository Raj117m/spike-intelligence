"""
Core data models for Category Intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Category:
    """A reusable category node."""

    id: str
    name: str
    parent: str | None = None
    aliases: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FactorType:
    """High-level type of an environmental factor."""

    id: str
    name: str
    description: str = ""


@dataclass(slots=True)
class ProductCategory:
    """Classification result for a product."""

    product: str
    primary: str
    secondary: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass(slots=True)
class SimilarityResult:
    """Similarity score between two products."""

    score: float
    matched_categories: list[str] = field(default_factory=list)
    explanation: str = ""


@dataclass(slots=True)
class ClassificationResult:
    """Automatic classification output."""

    product: str
    primary_category: str
    secondary_categories: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reason: str = ""
