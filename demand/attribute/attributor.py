"""Real-data attribution (v1 - lead/lag association) + a live watchlist.

For a spike in a product's attention, rank candidate ENVIRONMENTAL FACTORS by how
strongly and how early each rose beforehand:
  - analyze() does the math with no side effects (network reads only),
  - explain() resolves loose names, auto-discovers factors, and persists results,
  - watch() scans the trending firehose and reports, for each topic spiking now, the
    factor most likely driving it.

This is leading-indicator analysis (correlation + timing), NOT proof of causation.
"""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from ..detect.detector import find_spikes, robust_z
from ..ingest.wikipedia import fetch_series, related_titles, resolve_title, top_articles
from ..store.schema import connect, init_db

LEAD_DAYS = 14
MIN_FACTOR_Z = 2.0     # a factor must rise this many sigmas to count
LIVE_Z = 2.5           # "rising now" threshold for the forward signal


def attribute_spike(onset_idx: int, factor_z: dict[str, np.ndarray],
                    lead: int = LEAD_DAYS) -> list[dict]:
    """Rank factors by their peak rise in the [onset-lead, onset] window."""
    lo = max(0, onset_idx - lead)
    res = []
    for name, z in factor_z.items():
        win = z[lo:onset_idx + 1]
        if len(win) == 0:
            continue
        rel = int(np.argmax(win))
        res.append({"factor": name, "effect": float(win[rel]), "lag": int(onset_idx - (lo + rel))})
    cand = [r for r in res if r["effect"] >= MIN_FACTOR_Z]
    cand.sort(key=lambda r: -r["effect"])
    total = sum(r["effect"] for r in cand) or 1.0
    for r in cand:
        r["prob"] = r["effect"] / total
    return cand


def analyze(product: str, factor_titles: list[str], days: int = 180,
            k: float = 3.0, d: int = 2) -> dict:
    """Pure analysis: fetch product + factor series, align, detect spikes, attribute.
    No DB writes - safe to call many times (used by both explain() and watch())."""
    product = product.strip().replace(" ", "_")
    factor_titles = [t.strip().replace(" ", "_") for t in (factor_titles or []) if t and t.strip()]
    factor_titles = [t for t in dict.fromkeys(factor_titles) if t != product]

    p = fetch_series(product, days)
    if p.empty:
        return {"error": f"No Wikipedia data for '{product}'.", "product": product}

    series = {product: p.set_index("ts")["value"]}
    loaded, skipped = [], []
    for ft in factor_titles:
        s = fetch_series(ft, days)
        if s.empty:
            skipped.append(ft)
        else:
            series[ft] = s.set_index("ts")["value"]
            loaded.append(ft)

    df = pd.DataFrame(series).dropna()
    if len(df) < 30:
        return {"error": "Not enough overlapping daily data.", "product": product}

    dates = list(df.index)
    prod_vals = df[product].to_numpy()
    factor_z = {c: robust_z(df[c].to_numpy()) for c in df.columns if c != product}

    results = []
    for sp in find_spikes(prod_vals, k, d):
        t0 = sp["peak"]
        results.append({
            "onset": dates[t0], "magnitude": sp["magnitude"],
            "persistence": sp["persistence"], "acceleration": sp["acceleration"],
            "candidates": attribute_spike(t0, factor_z),
        })

    live = []
    for c, z in factor_z.items():
        recent = z[-5:]
        if len(recent) and float(np.max(recent)) >= LIVE_Z:
            live.append({"factor": c, "z": float(np.max(recent))})
    live.sort(key=lambda x: -x["z"])

    return {"product": product, "loaded": loaded, "skipped": skipped, "n_days": len(df),
            "last_date": dates[-1], "spikes": results, "live": live, "frame": df}


def explain(product: str, factor_titles: list[str], days: int = 180,
            k: float = 3.0, d: int = 2, con=None, resolve: bool = True) -> dict:
    """Resolve loose names, auto-discover factors if none given, analyze, and persist."""
    own = con is None
    con = con or connect()
    init_db(con)

    product_input = product
    if resolve:
        product = resolve_title(product) or product

    factor_titles = [t for t in (factor_titles or []) if t and t.strip()]
    auto = False
    if not factor_titles and resolve:
        factor_titles = related_titles(product.replace("_", " "))
        auto = True
    elif resolve:
        factor_titles = [resolve_title(t) or t for t in factor_titles]

    res = analyze(product, factor_titles, days=days, k=k, d=d)
    if "error" in res:
        if own:
            con.close()
        return {**res, "product_input": product_input, "auto_factors": auto}

    df = res["frame"]
    dates = list(df.index)
    product = res["product"]

    for tbl in ("observations", "factors", "_ground_truth", "spikes", "attributions"):
        con.execute(f"DELETE FROM {tbl}")
    obs = pd.DataFrame({"product_id": product, "segment": "ALL", "metric": "wiki_pageviews",
                        "source": "wikipedia", "ts": dates, "value": df[product].to_numpy()})
    con.register("inc", obs)
    con.execute("INSERT INTO observations SELECT * FROM inc")
    con.unregister("inc")

    frows = []
    for c in df.columns:
        if c == product:
            continue
        for dt, val in zip(dates, df[c].to_numpy()):
            frows.append((f"attention@{c}", "related_attention", "wikipedia", "ALL",
                          "wikipedia", dt, float(val)))
    if frows:
        fdf = pd.DataFrame(frows, columns=["factor_id", "category", "channel", "segment",
                                           "source", "ts", "value"])
        con.register("inc", fdf)
        con.execute("INSERT INTO factors SELECT * FROM inc")
        con.unregister("inc")

    now = datetime.now()
    srows, arows = [], []
    for sp in res["spikes"]:
        onset = sp["onset"]
        sid = f"{product}:{onset}"
        sev = sp["magnitude"] * sp["persistence"] * (1.0 + max(sp["acceleration"], 0.0))
        srows.append((sid, product, "ALL", onset, float(sev), sp["magnitude"],
                      sp["persistence"], sp["acceleration"], "assoc-v1"))
        for r in sp["candidates"]:
            arows.append((sid, f"attention@{r['factor']}", r["effect"], r["prob"],
                          r["lag"], "assoc-v1", now))
    if srows:
        sdf = pd.DataFrame(srows, columns=["spike_id", "product_id", "segment", "onset_ts",
                                           "severity", "magnitude", "persistence",
                                           "acceleration", "detector_version"])
        con.register("inc", sdf)
        con.execute("INSERT INTO spikes SELECT * FROM inc")
        con.unregister("inc")
    if arows:
        adf = pd.DataFrame(arows, columns=["spike_id", "factor_id", "effect_size",
                                           "posterior_incl_prob", "lag_days",
                                           "model_version", "run_ts"])
        con.register("inc", adf)
        con.execute("INSERT INTO attributions SELECT * FROM inc")
        con.unregister("inc")

    if own:
        con.close()
    return {"product": product, "product_input": product_input, "auto_factors": auto,
            "loaded": res["loaded"], "skipped": res["skipped"], "n_days": res["n_days"],
            "spikes": res["spikes"], "live": res["live"]}


def watch(limit: int = 10, days: int = 120, recent_days: int = 28,
          max_factors: int = 4, k: float = 3.0, d: int = 2) -> dict:
    """Scan the trending firehose; for each topic spiking in the last `recent_days`,
    auto-discover factors and report the most likely driver."""
    trending = top_articles(limit=limit)
    board, steady, scanned = [], 0, 0
    for name, views in trending:
        scanned += 1
        facs = related_titles(name.replace("_", " "), limit=max_factors)
        res = analyze(name, facs, days=days, k=k, d=d)
        if "error" in res or not res["spikes"]:
            continue
        last = pd.Timestamp(res["last_date"])
        recent = [sp for sp in res["spikes"]
                  if (last - pd.Timestamp(sp["onset"])).days <= recent_days]
        if not recent:
            steady += 1
            continue
        sp = max(recent, key=lambda x: pd.Timestamp(x["onset"]))
        top = sp["candidates"][0] if sp["candidates"] else None
        board.append({"topic": name, "views": views, "onset": sp["onset"],
                      "magnitude": sp["magnitude"], "reason": top})
    board.sort(key=lambda b: pd.Timestamp(b["onset"]), reverse=True)
    return {"board": board, "scanned": scanned, "steady": steady}
