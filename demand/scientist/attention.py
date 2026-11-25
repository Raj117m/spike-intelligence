"""
Attention estimation from Wikipedia pageviews.
"""

from statistics import mean


def estimate_attention(pageviews):
    if not pageviews:
        return 0.0

    values = [views for _, views in pageviews]
    return mean(values)


def peak_attention(pageviews):
    if not pageviews:
        return 0.0

    return max(views for _, views in pageviews)


def growth(pageviews):
    if len(pageviews) < 2:
        return 0.0

    first = pageviews[0][1]
    last = pageviews[-1][1]

    if first == 0:
        return 0.0

    return (last - first) / first
