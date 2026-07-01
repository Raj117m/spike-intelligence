"""Synthetic ground-truth generator.

Builds a universe of products whose demand proxy = trend + weekly seasonality + noise,
then injects spikes caused by *known* factors at *known* lags, plus decoy factors that
cause nothing. The hidden `_ground_truth` table lets Prompts 2-3 (Claude Code) score the
detector and attributor against truth before any paid API is used.
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from .base import Source

CATEGORIES = ["beauty", "gadgets", "home", "fitness", "pets"]
SEGMENTS = ["us_young", "us_old", "eu_young", "eu_old"]

# (factor_id, category|None=cross-industry, channel, segment|None=all,
#  causal, peak_z, lag_days, _reserved)
# peak_z = approximate height of the spike peak in residual sigmas (after de-seasonalizing),
# so the injected events genuinely match the spike definition (sharp + accelerating).
FACTORS = [
    ("viral_tiktok",      None,      "tiktok",  "us_young", True, 9.0, 4, 0),  # strong, cross-industry
    ("price_drop",        None,      "price",   None,       True, 6.0, 1, 0),
    ("heatwave",          "fitness", "weather", None,       True, 7.0, 2, 0),
    ("press_feature",     "gadgets", "news",    None,       True, 8.0, 3, 0),
    ("influencer_beauty", "beauty",  "tiktok",  "us_young", True, 8.0, 5, 0),
    ("pet_trend",         "pets",    "search",  None,       True, 7.0, 3, 0),
    ("decoy_news",        None,      "news",    None,       False, 0.0, 0, 0),
    ("decoy_weather",     None,      "weather", None,       False, 0.0, 0, 0),
    ("decoy_search",      None,      "search",  None,       False, 0.0, 0, 0),
]

# profile that ramps and accelerates into the peak, then decays (peak at index 2).
# Shoulders are high enough that a true spike clears the threshold for >=2 days.
SPIKE_PROFILE = (0.45, 0.85, 1.0, 0.85, 0.45)


class SyntheticSource(Source):
    def __init__(self, n_products: int = 500, days: int = 180, seed: int = 1):
        self.n_products = n_products
        self.days = days
        self.seed = seed

    def name(self) -> str:
        return "synthetic"

    def fetch(self) -> dict[str, pd.DataFrame]:
        rng = np.random.default_rng(self.seed)
        end = date.today()
        start = end - timedelta(days=self.days - 1)
        dates = pd.date_range(start, end, freq="D").date

        causal = [f for f in FACTORS if f[4]]
        decoys = [f for f in FACTORS if not f[4]]

        obs_rows, fac_rows, gt_rows = [], [], []

        for i in range(self.n_products):
            pid = f"P{i:04d}"
            cat = CATEGORIES[int(rng.integers(len(CATEGORIES)))]
            seg = SEGMENTS[int(rng.integers(len(SEGMENTS)))]
            base = float(rng.uniform(20, 60))
            trend = float(rng.normal(0, 0.05))
            amp = float(rng.uniform(1, 3))
            noise = float(rng.uniform(1, 2.5))

            t = np.arange(self.days)
            series = base + trend * t + amp * np.sin(2 * np.pi * t / 7)
            series = series + rng.normal(0, noise, self.days)

            # eligible causal factors: category matches (or cross) AND segment matches (or all)
            elig = [f for f in causal if f[1] in (None, cat) and f[3] in (None, seg)]
            n_fire = int(rng.integers(0, 3))  # 0, 1 or 2 real causes
            if elig and n_fire:
                pick = rng.choice(len(elig), size=min(n_fire, len(elig)), replace=False)
                for idx in np.atleast_1d(pick):
                    fid, fcat, chan, fseg, _, peak_z, lag, _r = elig[int(idx)]
                    fire_day = int(rng.integers(15, self.days - lag - 3))
                    fac_rows.append((fid, fcat or cat, chan, fseg or seg, "synthetic",
                                     dates[fire_day], 1.0))
                    onset = fire_day + lag  # peak (ground-truth) day
                    for j, p in enumerate(SPIKE_PROFILE):
                        k = onset - 2 + j
                        if 0 <= k < self.days:
                            series[k] += peak_z * noise * p
                    gt_rows.append((pid, seg, dates[onset], fid, lag))

            # decoy firings (recorded as factors, but cause no demand change)
            for _ in range(int(rng.integers(0, 2))):
                d = decoys[int(rng.integers(len(decoys)))]
                fire_day = int(rng.integers(10, self.days - 2))
                fac_rows.append((d[0], cat, d[2], seg, "synthetic", dates[fire_day], 1.0))

            for d in range(self.days):
                obs_rows.append((pid, seg, "demand_proxy", "synthetic",
                                 dates[d], float(series[d])))

        observations = pd.DataFrame(
            obs_rows, columns=["product_id", "segment", "metric", "source", "ts", "value"]
        )
        factors = pd.DataFrame(
            fac_rows,
            columns=["factor_id", "category", "channel", "segment", "source", "ts", "value"],
        )
        ground_truth = pd.DataFrame(
            gt_rows, columns=["product_id", "segment", "onset_ts", "factor_id", "lag_days"]
        )
        return {"observations": observations, "factors": factors, "_ground_truth": ground_truth}
