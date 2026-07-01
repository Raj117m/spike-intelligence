"""Offline tests for backtest_forecast: aggregate evaluation of the forecast strategy.

All network calls are monkeypatched.  The synthetic data mirrors the patterns used in
test_forecast.py so the two suites are comparable, but here we focus on the aggregate
numbers (recall, precision, lead time, lift) rather than which products surface.

The two-pass design means:
  Pass 1 — each factor is screened individually (lift >= min_lift gate).
  Pass 2 — qualifying factors are combined into one signal per product;
            evaluate_signal is called once so recall is not double-counted.
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd

import demand.forecast as fc

N = 300
SPIKE_DAYS_A = [60, 120, 180, 240]
SPIKE_DAYS_B = [55, 115, 175, 235]
LEAD = 5


def _dates(n: int = N) -> list[date]:
    return [date(2024, 1, 1) + timedelta(days=i) for i in range(n)]


def _df(vals: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame({"ts": _dates(len(vals)), "value": vals.copy()})


def _product_vals(rng: np.random.Generator,
                  spike_at: list[int] = SPIKE_DAYS_A) -> np.ndarray:
    v = 1000.0 + 150 * np.sin(2 * np.pi * np.arange(N) / 7) + rng.normal(0, 60, N)
    for s in spike_at:
        for j, p in enumerate((0.45, 0.85, 1.0, 0.85, 0.45)):
            idx = s - 2 + j
            if 0 <= idx < N:
                v[idx] += 900 * p
    return v


def _upstream_vals(rng: np.random.Generator,
                   spike_at: list[int] = SPIKE_DAYS_A) -> np.ndarray:
    """Factor rising LEAD days before each product spike — reliably predictive."""
    v = 800.0 + rng.normal(0, 40, N)
    for s in spike_at:
        for j, p in enumerate((0.6, 1.0, 0.6)):
            idx = s - LEAD - 1 + j
            if 0 <= idx < N:
                v[idx] += 700 * p
    return v


def _lagging_vals(rng: np.random.Generator,
                  spike_at: list[int] = SPIKE_DAYS_A) -> np.ndarray:
    """Factor rising 10 days AFTER each spike — lift ≈ 0, fails the gate."""
    v = 800.0 + rng.normal(0, 40, N)
    for s in spike_at:
        for j, p in enumerate((0.6, 1.0, 0.6)):
            idx = s + 10 + j
            if 0 <= idx < N:
                v[idx] += 700 * p
    return v


# ---------------------------------------------------------------------------
# Happy path: two products with reliable leading factors
# ---------------------------------------------------------------------------

def test_backtest_forecast_positive_lead_time(monkeypatch):
    """Two products each with a genuine leading factor → recall > 0, precision > base_rate,
    median lead > 0, beats_chance = True, has_positive_lead = True."""
    rng = np.random.default_rng(42)
    p1 = _product_vals(rng, SPIKE_DAYS_A)
    u1 = _upstream_vals(rng, SPIKE_DAYS_A)
    p2 = _product_vals(rng, SPIKE_DAYS_B)
    u2 = _upstream_vals(rng, SPIKE_DAYS_B)

    lookup = {"Prod1": p1, "Up1": u1, "Prod2": p2, "Up2": u2}

    monkeypatch.setattr(fc, "top_articles",
                        lambda limit=20: [("Prod1", 100_000), ("Prod2", 80_000)])
    monkeypatch.setattr(fc, "related_titles",
                        lambda title, limit=5: ["Up1"] if "Prod1" in title else ["Up2"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(lookup[title]))

    r = fc.backtest_forecast(days=N)

    assert r["n_qualifying"] == 2, f"both products should qualify, got {r['n_qualifying']}"
    assert r["total_spikes"] >= 4, "should accumulate product spikes from both products"
    assert r["recall"] is not None and r["recall"] > 0, \
        "at least some spikes should have been caught by the leading signal"
    assert r["precision"] is not None and r["precision"] > r["base_rate"], (
        f"precision {r['precision']:.2f} should exceed base rate {r['base_rate']:.2f}"
    )
    assert r["has_positive_lead"], \
        f"median lead should be > 0, got {r['median_lead']}"
    assert r["beats_chance"], \
        f"lift should be > 1, got {r['lift']}"


def test_backtest_forecast_aggregate_counts_are_consistent(monkeypatch):
    """total_hits <= total_signals and total_caught <= total_spikes (basic sanity)."""
    rng = np.random.default_rng(0)
    p1 = _product_vals(rng, SPIKE_DAYS_A)
    u1 = _upstream_vals(rng, SPIKE_DAYS_A)

    monkeypatch.setattr(fc, "top_articles",
                        lambda limit=20: [("Prod1", 100_000)])
    monkeypatch.setattr(fc, "related_titles",
                        lambda title, limit=5: ["Up1"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(p1 if title == "Prod1" else u1))

    r = fc.backtest_forecast(days=N)
    assert r["n_qualifying"] == 1
    assert r["total_hits"] <= r["total_signals"]
    assert r["total_caught"] <= r["total_spikes"]
    # precision and recall are in [0, 1]
    assert 0.0 <= r["precision"] <= 1.0
    assert 0.0 <= r["recall"] <= 1.0


# ---------------------------------------------------------------------------
# No qualifying drivers → empty aggregate
# ---------------------------------------------------------------------------

def test_backtest_forecast_no_qualifying_drivers(monkeypatch):
    """All related factors are lagging → none pass the lift gate → empty result."""
    rng = np.random.default_rng(1)
    prod_vals = _product_vals(rng)
    lag_vals = _lagging_vals(rng)

    monkeypatch.setattr(fc, "top_articles",
                        lambda limit=20: [("Prod", 50_000)])
    monkeypatch.setattr(fc, "related_titles",
                        lambda title, limit=5: ["Lagger"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(prod_vals if title == "Prod" else lag_vals))

    r = fc.backtest_forecast(days=N, min_lift=1.2)

    assert r["n_qualifying"] == 0
    assert r["total_spikes"] == 0
    assert r["precision"] is None
    assert r["recall"] is None
    assert not r["beats_chance"]
    assert not r["has_positive_lead"]


# ---------------------------------------------------------------------------
# Mixed: one good product, one with lagging factor → only good one counted
# ---------------------------------------------------------------------------

def test_backtest_forecast_mixed_products(monkeypatch):
    """One product with a leading factor and one with a lagging factor:
    only the good product appears in per_product; n_qualifying == 1."""
    rng = np.random.default_rng(7)
    good_prod = _product_vals(rng)
    good_up = _upstream_vals(rng)
    bad_prod = _product_vals(rng)
    bad_lag = _lagging_vals(rng)

    lookup = {"Good": good_prod, "GoodUp": good_up,
              "Bad": bad_prod, "BadUp": bad_lag}

    monkeypatch.setattr(fc, "top_articles",
                        lambda limit=20: [("Good", 100_000), ("Bad", 80_000)])
    monkeypatch.setattr(fc, "related_titles",
                        lambda title, limit=5: ["GoodUp"] if title == "Good" else ["BadUp"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(lookup[title]))

    r = fc.backtest_forecast(days=N, min_lift=1.2)

    assert r["n_qualifying"] == 1, f"only Good should qualify, got {r['n_qualifying']}"
    surfaced = [p["product"] for p in r["per_product"]]
    assert "Good" in surfaced
    assert "Bad" not in surfaced


# ---------------------------------------------------------------------------
# Insufficient spike history → excluded
# ---------------------------------------------------------------------------

def test_backtest_forecast_excludes_thin_spike_history(monkeypatch):
    """Product with only 1 detected spike is excluded (n_spikes < min_spikes=2)."""
    rng = np.random.default_rng(3)
    one_spike_vals = _product_vals(rng, spike_at=[120])   # single spike
    up_vals = _upstream_vals(rng, spike_at=[120])

    monkeypatch.setattr(fc, "top_articles",
                        lambda limit=20: [("OnePeak", 60_000)])
    monkeypatch.setattr(fc, "related_titles",
                        lambda title, limit=5: ["Upstream"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(one_spike_vals
                                                    if title == "OnePeak" else up_vals))

    r = fc.backtest_forecast(days=N, min_spikes=2)
    assert r["n_qualifying"] == 0
    assert r["n_products"] == 1   # was scanned but excluded
