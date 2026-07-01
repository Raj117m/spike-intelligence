"""Prompt 2 - the spike detector.

STL baseline (removes trend + weekly seasonality) -> residual -> robust z-score via
MAD -> fire when z >= k for >= d consecutive days AND the rise is accelerating. Writes
the `spikes` table, and scores detections against `_ground_truth` (synthetic only).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

from ..config import settings
from ..store.schema import connect, init_db


def robust_z(values: np.ndarray) -> np.ndarray:
    """De-seasonalize with STL, then standardize the residual robustly (MAD)."""
    s = pd.Series(np.asarray(values, dtype=float))
    resid = STL(s, period=7, robust=True).fit().resid
    med = float(resid.median())
    mad = float((resid - med).abs().median())
    sigma = 1.4826 * mad if mad > 0 else (float(resid.std()) or 1e-9)
    return ((resid - med) / sigma).to_numpy()


def find_spikes(values: np.ndarray, k: float, d: int) -> list[dict]:
    """Return spikes as runs of z>=k lasting >=d days with an accelerating onset."""
    z = robust_z(values)
    n = len(values)
    out: list[dict] = []
    i = 0
    while i < n:
        if z[i] >= k:
            j = i
            while j + 1 < n and z[j + 1] >= k:
                j += 1
            if (j - i + 1) >= d:
                peak = i + int(np.argmax(z[i:j + 1]))
                # accelerating rise: 2nd difference of the level at run start > 0
                if i >= 2:
                    accel = (values[i] - values[i - 1]) - (values[i - 1] - values[i - 2])
                else:
                    accel = 0.0
                if i < 2 or accel > 0:
                    out.append({
                        "peak": peak,
                        "magnitude": float(z[peak]),
                        "persistence": int(j - i + 1),
                        "acceleration": float(accel),
                    })
            i = j + 1
        else:
            i += 1
    return out


def detect(con=None, k: float | None = None, d: int | None = None) -> int:
    """Run the detector over all products; (re)write the `spikes` table. Returns count."""
    own = con is None
    con = con or connect()
    init_db(con)
    k = settings.spike_k if k is None else k
    d = settings.spike_min_days if d is None else d

    obs = con.execute(
        "SELECT product_id, segment, ts, value FROM observations ORDER BY product_id, ts"
    ).df()
    con.execute("DELETE FROM spikes")

    rows = []
    for pid, g in obs.groupby("product_id", sort=False):
        seg = g["segment"].iloc[0]
        vals = g["value"].to_numpy()
        dts = pd.to_datetime(g["ts"]).dt.date.to_numpy()
        for s in find_spikes(vals, k, d):
            onset = dts[s["peak"]]
            severity = s["magnitude"] * s["persistence"] * (1.0 + max(s["acceleration"], 0.0))
            rows.append((f"{pid}:{onset}", pid, seg, onset, float(severity),
                         s["magnitude"], s["persistence"], s["acceleration"],
                         settings.detector_version))

    if rows:
        df = pd.DataFrame(rows, columns=[
            "spike_id", "product_id", "segment", "onset_ts", "severity",
            "magnitude", "persistence", "acceleration", "detector_version"])
        con.register("inc", df)
        con.execute("INSERT INTO spikes SELECT * FROM inc")
        con.unregister("inc")

    if own:
        con.close()
    return len(rows)


def score(con=None, tol: int = 2) -> dict:
    """Compare detected spikes to `_ground_truth` (match within +/- tol days)."""
    own = con is None
    con = con or connect()
    det = con.execute("SELECT product_id, onset_ts FROM spikes").df()
    gt = con.execute("SELECT product_id, onset_ts FROM _ground_truth").df()
    if own:
        # keep connection open until we've read everything we need
        pass
    det["onset_ts"] = pd.to_datetime(det["onset_ts"])
    gt["onset_ts"] = pd.to_datetime(gt["onset_ts"])

    gt_by = {pid: g.copy() for pid, g in gt.groupby("product_id")}
    matched: set[tuple] = set()
    tp = 0
    for _, r in det.iterrows():
        cand = gt_by.get(r["product_id"])
        if cand is None:
            continue
        for idx, gr in cand.iterrows():
            if (r["product_id"], idx) in matched:
                continue
            if abs((gr["onset_ts"] - r["onset_ts"]).days) <= tol:
                matched.add((r["product_id"], idx))
                tp += 1
                break

    n_det, n_gt = len(det), len(gt)
    precision = tp / n_det if n_det else 0.0
    recall = tp / n_gt if n_gt else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    if own:
        con.close()
    return {"detected": n_det, "ground_truth": n_gt, "true_positives": tp,
            "precision": precision, "recall": recall, "f1": f1}
