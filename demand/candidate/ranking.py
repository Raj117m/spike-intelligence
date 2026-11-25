"""
Candidate Ranking Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(slots=True)
class Candidate:

    asin: str
    title: str

    reviews: int
    bought_last_month: int

    spike_score: float
    evidence_score: float
    confidence_score: float


def evidence_strength(reviews: int) -> float:
    """
    Maps review count onto a confidence scale.

    0 reviews -> 0

    grows smoothly toward 1
    """

    return 1.0 - math.exp(-reviews / 100.0)


def rank_candidate(
    asin: str,
    title: str,
    reviews: int,
    bought_last_month: int,
) -> Candidate:

    spike = bought_last_month / (reviews + 1)

    evidence = evidence_strength(reviews)

    confidence = spike * evidence

    return Candidate(
        asin=asin,
        title=title,
        reviews=reviews,
        bought_last_month=bought_last_month,
        spike_score=spike,
        evidence_score=evidence,
        confidence_score=confidence,
    )
