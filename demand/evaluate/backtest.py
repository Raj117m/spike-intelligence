"""Backtest the core claim: does a factor RISING actually predict the product's spike?

Causal walk-forward: each day a factor's TRAILING z-score (only days before it) crossing
a threshold is a SIGNAL predicting a spike in (t, t+lead]. We report precision, recall,
median lead time, base rate, and LIFT = precision / base rate. Lift > 1 means the signal
carries real information; lift ~ 1 means it doesn't.

`evaluate_signal` is the reusable core (works on plain arrays) so the radar can score
confidence without re-fetching.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..detect.detector import find_spikes
from ..ingest.wikipedia import fetch_series, related_titles, resolve_title


def trailing_z(values: np.ndarray, window: int = 28) -> np.ndarray:
    """Causal robust z: each day scored against the MAD of days strictly before it."""
    v = np.asarray(values, dtype=float)
    n = len(v)
    out = np.zeros(n)
    for t in range(window, n):
        w = v[t - window:t]
        med = float(np.median(w))
        mad = float(np.median(np.abs(w - med)))
        sigma = 1.4826 * mad if mad > 0 else (float(w.std()) or 1e-9)
        out[t] = (v[t] - med) / sigma
    return out


def _events(signal: np.ndarray, threshold: float) -> list[int]:
    on = signal >= threshold
    ev, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            ev.append(i)
            while i + 1 < n and on[i + 1]:
                i += 1
        i += 1
    return ev


def evaluate_signal(prod_vals, factor_arrays, lead=10, threshold=3.0,
                    window=28, k=3.0, d=2) -> dict:
    """Reusable scorer on plain arrays. Returns precision/recall/lead/base/lift."""
    prod_vals = np.asarray(prod_vals, dtype=float)
    n = len(prod_vals)
    spike_idx = sorted({sp["peak"] for sp in find_spikes(prod_vals, k, d)})
    res = {"n_spikes": len(spike_idx), "n_signals": 0, "precision": 0.0,
           "recall": 0.0, "median_lead": 0.0, "base_rate": 0.0, "lift": None}
    if not spike_idx:
        return res

    if factor_arrays:
        signal = np.vstack([trailing_z(np.asarray(f, float), window)
                            for f in factor_arrays]).max(axis=0)
    else:
        signal = np.zeros(n)
    events = _events(signal, threshold)

    def has_spike(t):
        return any(t < s <= t + lead for s in spike_idx)

    hits = sum(1 for t in events if has_spike(t))
    precision = hits / len(events) if events else 0.0
    caught, leads = 0, []
    for s in spike_idx:
        pre = [t for t in events if s - lead <= t <= s - 1]
        if pre:
            caught += 1
            leads.append(s - max(pre))
    recall = caught / len(spike_idx)
    valid = list(range(window, n - 1))
    base = (sum(1 for t in valid if has_spike(t)) / len(valid)) if valid else 0.0
    res.update({"n_signals": len(events), "precision": precision, "recall": recall,
                "median_lead": float(np.median(leads)) if leads else 0.0,
                "base_rate": base, "lift": (precision / base) if base > 0 else None})
    return res


def backtest(product, factor_titles, days=365, lead=10, threshold=3.0,
             window=28, k=3.0, d=2, resolve=True) -> dict:
    if resolve:
        product = resolve_title(product) or product
        if not factor_titles:
            factor_titles = related_titles(product.replace("_", " "))
        else:
            factor_titles = [resolve_title(t) or t for t in factor_titles]
    product = product.strip().replace(" ", "_")
    factor_titles = [t.strip().replace(" ", "_") for t in (factor_titles or []) if t and t.strip()]
    factor_titles = [t for t in dict.fromkeys(factor_titles) if t != product]

    p = fetch_series(product, days)
    if p.empty:
        return {"error": f"No data for '{product}'."}
    series = {product: p.set_index("ts")["value"]}
    loaded = []
    for ft in factor_titles:
        s = fetch_series(ft, days)
        if not s.empty:
            series[ft] = s.set_index("ts")["value"]
            loaded.append(ft)
    df = pd.DataFrame(series).dropna()
    if len(df) < window + 30:
        return {"error": "Not enough history to backtest.", "loaded": loaded}

    ev = evaluate_signal(df[product].to_numpy(), [df[c].to_numpy() for c in loaded],
                         lead=lead, threshold=threshold, window=window, k=k, d=d)
    if ev["n_spikes"] == 0:
        return {"error": "No spikes in the product's history to test against.", "loaded": loaded}
    return {"product": product, "loaded": loaded, "n_days": len(df),
            "lead_window": lead, "threshold": threshold, **ev}
