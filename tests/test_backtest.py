"""Backtest test: a genuinely LEADING factor should show lift > 1 and decent recall;
a LAGGING factor (rises only after spikes) should not predict them. No network."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

import demand.evaluate.backtest as bt

N = 300
SPIKES = [40, 90, 130, 175, 220, 265]
PROFILE = (0.45, 0.85, 1.0, 0.85, 0.45)


def _product(rng):
    v = 1000 + 150 * np.sin(2 * np.pi * np.arange(N) / 7) + rng.normal(0, 60, N)
    for s in SPIKES:
        for j, p in enumerate(PROFILE):
            v[s - 2 + j] += 900 * p
    return v


def _factor(rng, offset):
    """Flat series with a sharp bump `offset` days from each product spike."""
    v = 800 + rng.normal(0, 40, N)
    for s in SPIKES:
        c = s + offset
        for j, p in enumerate((0.6, 1.0, 0.6)):
            if 0 <= c - 1 + j < N:
                v[c - 1 + j] += 700 * p
    return v


def _patch(monkeypatch, table):
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(N)]
    monkeypatch.setattr(bt, "fetch_series",
                        lambda title, days=180: pd.DataFrame({"ts": dates, "value": table[title]}))


def test_leading_factor_has_lift(monkeypatch):
    rng = np.random.default_rng(0)
    _patch(monkeypatch, {"Prod": _product(rng), "Lead": _factor(rng, offset=-5)})
    r = bt.backtest("Prod", ["Lead"], days=N, lead=10, threshold=3.0, resolve=False)
    assert "error" not in r
    assert r["n_spikes"] >= 5
    assert r["recall"] >= 0.6
    assert r["lift"] >= 1.5
    assert 3 <= r["median_lead"] <= 8


def test_lagging_factor_does_not_predict(monkeypatch):
    rng = np.random.default_rng(0)
    _patch(monkeypatch, {"Prod": _product(rng), "Lag": _factor(rng, offset=+3)})
    r = bt.backtest("Prod", ["Lag"], days=N, lead=10, threshold=3.0, resolve=False)
    assert "error" not in r
    assert r["recall"] <= 0.34          # a factor that rises AFTER spikes can't predict them
