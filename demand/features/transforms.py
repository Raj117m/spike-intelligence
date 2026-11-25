"""
Feature transformations.
"""

from __future__ import annotations

import numpy as np

from .models import Feature


def zscore(values: list[float]) -> list[float]:

    if len(values) < 2:
        return [0.0 for _ in values]

    arr = np.asarray(values, dtype=float)

    std = arr.std()

    if std == 0:
        return [0.0 for _ in values]

    return ((arr - arr.mean()) / std).tolist()


def normalize(features: list[Feature]) -> list[Feature]:

    values = [f.value for f in features]

    scaled = zscore(values)

    result = []

    for feature, value in zip(features, scaled):

        result.append(
            Feature(
                topic=feature.topic,
                source=feature.source,
                name=f"{feature.name}_zscore",
                value=float(value),
                signal=feature.signal,
            )
        )

    return result
