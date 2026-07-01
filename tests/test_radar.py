"""Radar test: a topic whose historically-reliable factor is rising now should appear as
a PROVEN forward opportunity; a flat topic should not. A report file is written. Offline."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

import demand.attribute.attributor as att
import demand.radar as radar

N = 300
SPIKES = [60, 120, 180, 240]


def _product(rng):
    v = 1000 + 150 * np.sin(2 * np.pi * np.arange(N) / 7) + rng.normal(0, 60, N)
    for s in SPIKES:
        for j, p in enumerate((0.45, 0.85, 1.0, 0.85, 0.45)):
            v[s - 2 + j] += 900 * p
    return v


def _lead(rng):
    v = 800 + rng.normal(0, 40, N)
    for s in SPIKES:                      # leads each historical spike by 5 days
        for j, p in enumerate((0.6, 1.0, 0.6)):
            v[s - 5 - 1 + j] += 700 * p
    for j, p in enumerate((0.6, 1.0, 0.6)):   # ...and is rising NOW (near the end)
        if 296 - 1 + j < N:
            v[296 - 1 + j] += 700 * p
    return v


def test_radar_flags_proven_opportunity_and_writes_report(monkeypatch, tmp_path):
    rng = np.random.default_rng(0)
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(N)]
    table = {"Prod": _product(rng), "Lead": _lead(rng),
             "Boring": 800 + rng.normal(0, 40, N)}

    monkeypatch.setattr(att, "fetch_series",
                        lambda title, days=180: pd.DataFrame({"ts": dates, "value": table[title]}))
    monkeypatch.setattr(radar, "top_articles",
                        lambda limit=8: [("Prod", 100000), ("Boring", 50000)])
    monkeypatch.setattr(radar, "related_titles",
                        lambda title, limit=3: ["Lead"] if title.replace(" ", "_") == "Prod" else [])

    r = radar.radar(days=N, reports_dir=str(tmp_path), score=False)

    topics = [o["topic"] for o in r["opportunities"]]
    assert "Prod" in topics
    assert "Boring" not in topics
    prod = next(o for o in r["opportunities"] if o["topic"] == "Prod")
    assert prod["confidence"] == "proven"
    assert prod["lift"] is not None and prod["lift"] >= 1.2
    # a dated report file was written
    import os
    assert os.path.exists(r["report_path"])
