"""Watchlist test: a recently-spiking trending topic should appear on the board with
its leading factor identified. Network is monkeypatched."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

import demand.attribute.attributor as att

N = 120


def _series(spike_at=None):
    rng = np.random.default_rng(2)
    v = 1000 + 150 * np.sin(2 * np.pi * np.arange(N) / 7) + rng.normal(0, 60, N)
    if spike_at is not None:
        for j, p in enumerate((0.45, 0.85, 1.0, 0.85, 0.45)):
            v[spike_at - 2 + j] += 900 * p
    return v


def test_watch_lists_spiking_topic_and_driver(monkeypatch):
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(N)]
    table = {
        "Prod": _series(spike_at=N - 10),    # recent spike, ~10 days before the end
        "Lead": _series(spike_at=N - 14),    # leads the spike by ~4 days
        "Boring": _series(spike_at=None),    # steady, no spike
    }

    monkeypatch.setattr(att, "fetch_series",
                        lambda title, days=180: pd.DataFrame({"ts": dates, "value": table[title]}))
    monkeypatch.setattr(att, "top_articles",
                        lambda limit=10: [("Prod", 100000), ("Boring", 50000)])
    monkeypatch.setattr(att, "related_titles",
                        lambda title, limit=4: ["Lead"] if title.replace(" ", "_") == "Prod" else [])

    r = att.watch(limit=10, days=N, recent_days=28)
    topics = [b["topic"] for b in r["board"]]
    assert "Prod" in topics            # spiking topic is surfaced
    assert "Boring" not in topics      # steady topic is not
    entry = next(b for b in r["board"] if b["topic"] == "Prod")
    assert entry["reason"] and entry["reason"]["factor"] == "Lead"
    assert entry["reason"]["lag"] >= 1
