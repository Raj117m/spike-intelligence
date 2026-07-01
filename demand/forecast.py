"""Early-warning forecast: surface products NOT yet spiking whose related topics
are rising now in a pattern that has historically preceded their spikes.

Algorithm
---------
For each trending product:
  1. Skip if the product is already spiking (recent spike peak within recent_spike_days).
  2. Require >= min_spikes historical spikes so any lift figure is trustworthy.
  3. Fetch related topics (auto-discovered via `related_titles`).
  4. For each related topic compute:
       current_rise    = max trailing-z in the last few days (is it rising NOW?)
       historical_lift = lift from evaluate_signal            (has it reliably led past spikes?)
  5. A factor qualifies only when ALL THREE gates pass:
       - current_rise >= min_z      (it is actually rising now)
       - lift is not None           (enough history to compute reliability)
       - lift >= min_lift           (it has been reliably predictive, not below-chance noise)
  6. early_score = Σ (current_rise × lift) over qualifying factors only.
  7. Drop any product with no qualifying factor.

Output is sorted by early_score descending.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .detect.detector import find_spikes
from .evaluate.backtest import evaluate_signal, trailing_z
from .ingest.wikipedia import fetch_series, related_titles, top_articles

# Minimum trailing-z in the last few days for a factor to count as "rising now".
MIN_CURRENT_Z: float = 1.5
# Minimum historical lift required for a factor to be trusted as predictive.
MIN_LIFT: float = 1.2
# Product must have at least this many historical spikes for lift to be meaningful.
MIN_SPIKES: int = 2
# A spike peak within this many days of today means the product is already spiking.
_SPIKE_RECENCY: int = 14


def _current_rise(vals: np.ndarray, window: int = 28, recent: int = 5) -> float:
    """Max trailing-z in the last `recent` days; positive means the series is rising."""
    z = trailing_z(vals, window)
    return float(np.max(z[-recent:])) if len(z) >= recent else 0.0


def forecast(limit: int = 10, days: int = 365, max_factors: int = 5,
             lead: int = 10, threshold: float = 3.0,
             min_z: float = MIN_CURRENT_Z, min_lift: float = MIN_LIFT,
             min_spikes: int = MIN_SPIKES, k: float = 3.0, d: int = 2,
             recent_spike_days: int = _SPIKE_RECENCY) -> list[dict]:
    """Scan trending articles; return reliability-gated early-warning opportunities.

    A factor contributes to a product's early_score ONLY when it passes all three gates:
    rising now (current_z >= min_z), historically predictive (lift >= min_lift), and the
    product has enough past spikes for that lift to be trustworthy (n_spikes >= min_spikes).

    Each entry in the returned list contains:
        product, views, n_spikes, early_score,
        best_driver, best_driver_z, best_driver_lift, expected_lead_days,
        factors (all related-topic details, sorted best-first)
    """
    opportunities: list[dict] = []

    for name, views in top_articles(limit):
        prod_df = fetch_series(name, days)
        if prod_df.empty or len(prod_df) < 30:
            continue

        prod_series = prod_df.set_index("ts")["value"]
        prod_vals = prod_series.to_numpy()

        # Detect spikes once; use the result for both criteria below.
        prod_spikes = find_spikes(prod_vals, k, d)

        # Criterion 1: product must not already be spiking right now.
        if any(sp["peak"] >= len(prod_vals) - recent_spike_days for sp in prod_spikes):
            continue

        # Criterion 2: enough historical spikes for any lift figure to be meaningful.
        n_prod_spikes = len(prod_spikes)
        if n_prod_spikes < min_spikes:
            continue

        factor_titles = related_titles(name.replace("_", " "), limit=max_factors)
        factor_rows: list[dict] = []

        for ft in factor_titles:
            fdf = fetch_series(ft, days)
            if fdf.empty:
                continue
            # Align product and factor on shared dates; drop any gaps.
            aligned = pd.DataFrame(
                {"prod": prod_series, "fac": fdf.set_index("ts")["value"]}
            ).dropna()
            if len(aligned) < 30:
                continue

            pvals = aligned["prod"].to_numpy()
            fvals = aligned["fac"].to_numpy()

            cur_z = _current_rise(fvals)
            ev = evaluate_signal(pvals, [fvals], lead=lead, threshold=threshold)
            lift = ev.get("lift")
            med_lead = ev.get("median_lead", 0.0)
            score = cur_z * lift if (lift is not None and lift > 0) else 0.0

            factor_rows.append({
                "factor": ft,
                "current_z": cur_z,
                "lift": lift,
                "median_lead": med_lead,
                "score": score,
            })

        # Criterion 3: at least one factor must clear all three gates.
        active = [
            f for f in factor_rows
            if f["current_z"] >= min_z
            and f["lift"] is not None
            and f["lift"] >= min_lift
        ]
        if not active:
            continue

        early_score = sum(f["score"] for f in active)
        best = max(active, key=lambda f: f["score"])
        opportunities.append({
            "product": name,
            "views": views,
            "n_spikes": n_prod_spikes,
            "early_score": early_score,
            "best_driver": best["factor"],
            "best_driver_z": best["current_z"],
            "best_driver_lift": best["lift"],
            "expected_lead_days": best["median_lead"],
            "factors": sorted(factor_rows, key=lambda f: -f["score"]),
        })

    return sorted(opportunities, key=lambda o: -o["early_score"])


def backtest_forecast(
    limit: int = 20,
    days: int = 365,
    max_factors: int = 5,
    lead: int = 10,
    threshold: float = 3.0,
    min_lift: float = MIN_LIFT,
    min_spikes: int = MIN_SPIKES,
    k: float = 3.0,
    d: int = 2,
) -> dict:
    """Aggregate backtest of the forecast strategy across trending products.

    For each product with >= min_spikes historical spikes, screen its related
    topics individually (lift >= min_lift gate), then combine the qualifying
    factors into a single signal and call evaluate_signal once per product —
    so the combined signal fires when ANY qualifying factor exceeds threshold,
    and recall is counted without double-counting.

    Aggregation (micro-averaged across products):
      precision  = total signal-hits / total signals
      recall     = total spikes-caught / total spikes
      median_lead = median of per-product median lead times
      base_rate  = mean of per-product base rates
      lift       = precision / base_rate

    Returns a dict with aggregate stats and a 'per_product' breakdown list.
    Keys: n_products, n_qualifying, total_spikes, total_signals,
          total_hits, total_caught, precision, recall, median_lead,
          base_rate, lift, beats_chance, has_positive_lead, per_product.
    """
    n_products = 0
    per_product: list[dict] = []

    for name, _views in top_articles(limit):
        prod_df = fetch_series(name, days)
        if prod_df.empty or len(prod_df) < 30:
            continue
        n_products += 1

        prod_series = prod_df.set_index("ts")["value"]
        prod_vals = prod_series.to_numpy()

        n_prod_spikes = len(find_spikes(prod_vals, k, d))
        if n_prod_spikes < min_spikes:
            continue

        # Pass 1: screen each related factor individually against the lift gate.
        factor_titles = related_titles(name.replace("_", " "), limit=max_factors)
        qualifying_fseries: dict[str, pd.Series] = {}
        for ft in factor_titles:
            fdf = fetch_series(ft, days)
            if fdf.empty:
                continue
            pairwise = pd.DataFrame(
                {"prod": prod_series, "fac": fdf.set_index("ts")["value"]}
            ).dropna()
            if len(pairwise) < 30:
                continue
            ev_check = evaluate_signal(
                pairwise["prod"].to_numpy(),
                [pairwise["fac"].to_numpy()],
                lead=lead, threshold=threshold,
            )
            if ev_check.get("lift") is not None and ev_check["lift"] >= min_lift:
                qualifying_fseries[ft] = fdf.set_index("ts")["value"]

        if not qualifying_fseries:
            continue

        # Pass 2: align product + all qualifying factors; one combined evaluation.
        combined = pd.DataFrame({"prod": prod_series, **qualifying_fseries}).dropna()
        if len(combined) < 30:
            continue

        ev = evaluate_signal(
            combined["prod"].to_numpy(),
            [combined[col].to_numpy() for col in qualifying_fseries],
            lead=lead, threshold=threshold,
        )
        per_product.append({
            "product": name,
            "n_qualifying_factors": len(qualifying_fseries),
            "n_spikes": ev["n_spikes"],
            "n_signals": ev["n_signals"],
            "precision": ev["precision"],
            "recall": ev["recall"],
            "median_lead": ev["median_lead"],
            "base_rate": ev["base_rate"],
            "lift": ev["lift"],
        })

    if not per_product:
        return {
            "n_products": n_products, "n_qualifying": 0,
            "total_spikes": 0, "total_signals": 0,
            "total_hits": 0, "total_caught": 0,
            "precision": None, "recall": None, "median_lead": None,
            "base_rate": None, "lift": None,
            "beats_chance": False, "has_positive_lead": False,
            "per_product": [],
        }

    total_spikes = sum(p["n_spikes"] for p in per_product)
    total_signals = sum(p["n_signals"] for p in per_product)
    # Reconstruct integer counts from the fractional precision/recall.
    total_hits = sum(round(p["precision"] * p["n_signals"]) for p in per_product)
    total_caught = sum(round(p["recall"] * p["n_spikes"]) for p in per_product)

    agg_precision = total_hits / total_signals if total_signals > 0 else 0.0
    agg_recall = total_caught / total_spikes if total_spikes > 0 else 0.0
    lead_times = [p["median_lead"] for p in per_product if p["median_lead"] > 0]
    agg_median_lead = float(np.median(lead_times)) if lead_times else 0.0
    base_rates = [p["base_rate"] for p in per_product if p["base_rate"] > 0]
    agg_base_rate = float(np.mean(base_rates)) if base_rates else 0.0
    agg_lift = agg_precision / agg_base_rate if agg_base_rate > 0 else None

    return {
        "n_products": n_products,
        "n_qualifying": len(per_product),
        "total_spikes": total_spikes,
        "total_signals": total_signals,
        "total_hits": total_hits,
        "total_caught": total_caught,
        "precision": agg_precision,
        "recall": agg_recall,
        "median_lead": agg_median_lead,
        "base_rate": agg_base_rate,
        "lift": agg_lift,
        "beats_chance": agg_lift is not None and agg_lift > 1.0,
        "has_positive_lead": agg_median_lead > 0,
        "per_product": per_product,
    }
