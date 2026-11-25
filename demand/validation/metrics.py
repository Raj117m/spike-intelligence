"""
Prediction evaluation metrics.
"""

from __future__ import annotations


def precision(tp: int, fp: int) -> float:
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)


def recall(tp: int, fn: int) -> float:
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)


def f1(tp: int, fp: int, fn: int) -> float:
    p = precision(tp, fp)
    r = recall(tp, fn)

    if p + r == 0:
        return 0.0

    return 2 * p * r / (p + r)
