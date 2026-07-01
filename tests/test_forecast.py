"""Offline tests for the early-warning forecast feature.

All network calls (top_articles, related_titles, fetch_series) are monkeypatched.

Three gates are enforced on every factor before it contributes to the early score:
  1. current_z >= min_z        — the factor must actually be rising right now
  2. lift >= min_lift          — it must have reliably predicted past spikes (not below chance)
  3. n_prod_spikes >= min_spikes — the product needs enough historical spikes for lift to mean anything

The synthetic data is designed so that:
  - A 'good' upstream factor reliably rises ~5 days before each product spike (lift >> 1.2).
  - The 'good' factor is also rising right now (high trailing-z at the end of the series).
  - A 'bad' driver rises AFTER spikes (lift ≈ 0) — loud but unreliable.
  - The product itself is NOT currently spiking (last spike is well before the window end).
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

import demand.forecast as fc

N = 300          # length of all synthetic series
SPIKE_DAYS = [60, 120, 180, 240]   # product spikes here; last is 59 days from series end
LEAD = 5         # good upstream factor leads each product spike by this many days


def _dates(n: int = N) -> list[date]:
    start = date(2024, 1, 1)
    return [start + timedelta(days=i) for i in range(n)]


def _df(vals: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame({"ts": _dates(len(vals)), "value": vals.copy()})


def _product_vals(rng: np.random.Generator,
                  spike_at: list[int] = SPIKE_DAYS) -> np.ndarray:
    """Weekly-seasonal baseline with clear spikes well before the series end."""
    v = 1000.0 + 150 * np.sin(2 * np.pi * np.arange(N) / 7) + rng.normal(0, 60, N)
    for s in spike_at:
        for j, p in enumerate((0.45, 0.85, 1.0, 0.85, 0.45)):
            idx = s - 2 + j
            if 0 <= idx < N:
                v[idx] += 900 * p
    return v


def _upstream_vals(rng: np.random.Generator, rising_now: bool = True) -> np.ndarray:
    """Factor that reliably rises LEAD days before each product spike.
    Optionally also rising in the last few days (the live early-warning signal)."""
    v = 800.0 + rng.normal(0, 40, N)
    for s in SPIKE_DAYS:
        for j, p in enumerate((0.6, 1.0, 0.6)):
            idx = s - LEAD - 1 + j
            if 0 <= idx < N:
                v[idx] += 700 * p
    if rising_now:
        for j, p in enumerate((0.6, 1.0, 0.6)):
            idx = N - 4 + j
            if 0 <= idx < N:
                v[idx] += 700 * p
    return v


def _lagging_vals(rng: np.random.Generator) -> np.ndarray:
    """Factor that rises 10 days AFTER each product spike — a lagging, not leading, signal.
    evaluate_signal gives this lift ≈ 0 because its signals do NOT precede spikes."""
    v = 800.0 + rng.normal(0, 40, N)
    for s in SPIKE_DAYS:
        for j, p in enumerate((0.6, 1.0, 0.6)):
            idx = s + 10 + j    # rises well AFTER the spike
            if 0 <= idx < N:
                v[idx] += 700 * p
    # Also rising hard right now — without the lift gate this would score very high
    for j, p in enumerate((0.6, 1.0, 0.6)):
        idx = N - 4 + j
        if 0 <= idx < N:
            v[idx] += 700 * p
    return v


# ---------------------------------------------------------------------------
# Happy path: upstream rising now + historically reliable → product surfaces
# ---------------------------------------------------------------------------

def test_forecast_surfaces_pre_spike_signal(monkeypatch):
    """Good upstream factor (rising now, lift >> 1.2) surfaces the product."""
    rng = np.random.default_rng(42)
    prod_vals = _product_vals(rng)
    up_vals = _upstream_vals(rng, rising_now=True)

    monkeypatch.setattr(fc, "top_articles", lambda limit=10: [("Widget", 100_000)])
    monkeypatch.setattr(fc, "related_titles", lambda title, limit=5: ["Upstream"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(prod_vals if title == "Widget" else up_vals))

    results = fc.forecast(days=N)

    products = [r["product"] for r in results]
    assert "Widget" in products, f"Expected Widget in forecast output, got: {products}"

    entry = next(r for r in results if r["product"] == "Widget")
    assert entry["best_driver"] == "Upstream"
    assert entry["best_driver_z"] > fc.MIN_CURRENT_Z
    assert entry["early_score"] > 0


def test_forecast_best_driver_has_lift_above_threshold(monkeypatch):
    """The qualifying driver must have lift >= MIN_LIFT (here >> 1.2)."""
    rng = np.random.default_rng(0)
    prod_vals = _product_vals(rng)
    up_vals = _upstream_vals(rng, rising_now=True)

    monkeypatch.setattr(fc, "top_articles", lambda limit=10: [("Widget", 100_000)])
    monkeypatch.setattr(fc, "related_titles", lambda title, limit=5: ["Upstream"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(prod_vals if title == "Widget" else up_vals))

    results = fc.forecast(days=N)
    assert results, "Expected at least one opportunity"
    lift = results[0]["best_driver_lift"]
    assert lift is not None and lift >= fc.MIN_LIFT, f"Expected lift >= {fc.MIN_LIFT}, got {lift}"


# ---------------------------------------------------------------------------
# Exclusion 1: product already spiking → must not appear
# ---------------------------------------------------------------------------

def test_forecast_excludes_already_spiking(monkeypatch):
    """Product with a spike RIGHT NOW (within _SPIKE_RECENCY days) is excluded."""
    rng = np.random.default_rng(42)
    v = 1000.0 + 150 * np.sin(2 * np.pi * np.arange(N) / 7) + rng.normal(0, 60, N)
    for j, p in enumerate((0.45, 0.85, 1.0, 0.85, 0.45)):
        idx = N - 7 + j   # peak at N-5=295; _SPIKE_RECENCY window is 14 days
        if 0 <= idx < N:
            v[idx] += 1200 * p

    monkeypatch.setattr(fc, "top_articles", lambda limit=10: [("Spiking", 200_000)])
    monkeypatch.setattr(fc, "related_titles", lambda title, limit=5: [])
    monkeypatch.setattr(fc, "fetch_series", lambda title, days=365: _df(v))

    results = fc.forecast(days=N)
    assert all(r["product"] != "Spiking" for r in results), \
        "Currently-spiking product must be excluded"


# ---------------------------------------------------------------------------
# Exclusion 2: factor is flat (not rising now) → product must not surface
# ---------------------------------------------------------------------------

def test_forecast_excludes_flat_factor(monkeypatch):
    """Related topic is perfectly flat → current_z = 0 → gate 1 fails → excluded."""
    rng = np.random.default_rng(99)
    prod_vals = _product_vals(rng)
    flat_vals = np.full(N, 800.0)   # constant; trailing-z is always 0

    monkeypatch.setattr(fc, "top_articles", lambda limit=10: [("Quiet", 80_000)])
    monkeypatch.setattr(fc, "related_titles", lambda title, limit=5: ["FlatFactor"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(prod_vals if title == "Quiet" else flat_vals))

    results = fc.forecast(days=N)
    assert all(r["product"] != "Quiet" for r in results), \
        "Product with flat related topic must not appear"


# ---------------------------------------------------------------------------
# Exclusion 3: driver rising hard but lift < 1 → must NOT surface (key new gate)
# ---------------------------------------------------------------------------

def test_forecast_excludes_below_chance_driver(monkeypatch):
    """A lagging factor rising hard now but with lift ≈ 0 must not surface its product.

    The lagging driver fires signals AFTER product spikes, so precision ≈ 0 and
    lift ≈ 0 < min_lift=1.2.  Without the lift gate this product would rank #1
    (its raw current_z is ~17).  With the gate it is excluded entirely.
    """
    rng = np.random.default_rng(13)
    prod_vals = _product_vals(rng)
    bad_vals = _lagging_vals(rng)

    monkeypatch.setattr(fc, "top_articles", lambda limit=10: [("Victim", 150_000)])
    monkeypatch.setattr(fc, "related_titles", lambda title, limit=5: ["BadDriver"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(prod_vals if title == "Victim" else bad_vals))

    results = fc.forecast(days=N, min_lift=1.2)
    assert all(r["product"] != "Victim" for r in results), (
        "Product whose only driver has lift < 1 must be excluded "
        "even when that driver is rising hard right now"
    )


# ---------------------------------------------------------------------------
# Exclusion 4: too few historical spikes → lift is unreliable → excluded
# ---------------------------------------------------------------------------

def test_forecast_excludes_insufficient_spike_history(monkeypatch):
    """Product with only 1 historical spike: lift computed from a single event is
    meaningless, so the product is excluded regardless of how strong the factor looks."""
    rng = np.random.default_rng(55)
    # Only ONE spike, at day 120
    one_spike_vals = _product_vals(rng, spike_at=[120])
    up_vals = _upstream_vals(rng, rising_now=True)

    monkeypatch.setattr(fc, "top_articles", lambda limit=10: [("OnePeak", 70_000)])
    monkeypatch.setattr(fc, "related_titles", lambda title, limit=5: ["Upstream"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(one_spike_vals if title == "OnePeak"
                                                    else up_vals))

    results = fc.forecast(days=N, min_spikes=2)
    assert all(r["product"] != "OnePeak" for r in results), \
        "Product with only 1 historical spike must be excluded (lift is unreliable)"


# ---------------------------------------------------------------------------
# Ranking: highest-scoring qualifying factor wins best_driver
# ---------------------------------------------------------------------------

def test_forecast_best_driver_is_highest_scoring_factor(monkeypatch):
    """When a reliable driver and a flat driver coexist, the reliable one is best_driver."""
    rng = np.random.default_rng(7)
    prod_vals = _product_vals(rng)
    strong_vals = _upstream_vals(rng, rising_now=True)  # qualifies: high z + high lift
    flat_vals = np.full(N, 800.0)                        # fails gate 1 (z=0) and gate 2

    lookup = {"Prod": prod_vals, "Strong": strong_vals, "Flat": flat_vals}

    monkeypatch.setattr(fc, "top_articles", lambda limit=10: [("Prod", 90_000)])
    monkeypatch.setattr(fc, "related_titles", lambda title, limit=5: ["Strong", "Flat"])
    monkeypatch.setattr(fc, "fetch_series",
                        lambda title, days=365: _df(lookup[title]))

    results = fc.forecast(days=N, min_z=1.0)
    assert results, "Expected Prod to surface — Strong is rising and historically reliable"
    assert results[0]["best_driver"] == "Strong"
