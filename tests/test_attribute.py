"""Attribution test: with a known leading factor, the engine should pick it as the
top reason for the spike. No network - fetch_series is monkeypatched."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

import demand.attribute.attributor as att
from demand.store.schema import connect, init_db

N = 180
SPIKE = 120


def _base(rng):
    return 1000 + 150 * np.sin(2 * np.pi * np.arange(N) / 7) + rng.normal(0, 60, N)


def _build():
    rng = np.random.default_rng(0)
    prod = _base(rng)
    for j, p in enumerate((0.45, 0.85, 1.0, 0.85, 0.45)):      # product spike at SPIKE
        prod[SPIKE - 2 + j] += 900 * p
    lead = _base(rng)
    for j, p in enumerate((0.5, 0.8, 1.0, 0.6)):               # leader rises ~4 days earlier
        lead[(SPIKE - 4) - 1 + j] += 800 * p
    flat = _base(rng)                                          # unrelated factor
    return prod, lead, flat


def test_attribution_picks_the_leading_factor(monkeypatch, tmp_path):
    prod, lead, flat = _build()
    start = date(2024, 1, 1)
    dates = [start + timedelta(days=i) for i in range(N)]
    table = {"Prod": prod, "Lead": lead, "Flat": flat}

    def fake_fetch(title, days=180):
        return pd.DataFrame({"ts": [d for d in dates], "value": table[title]})

    monkeypatch.setattr(att, "fetch_series", fake_fetch)

    con = connect(tmp_path / "a.duckdb")
    init_db(con)
    r = att.explain("Prod", ["Lead", "Flat"], days=N, con=con, resolve=False)

    assert "error" not in r
    assert r["spikes"], "no spike detected"
    target = dates[SPIKE]
    near = [s for s in r["spikes"] if abs((pd.Timestamp(s["onset"]) - pd.Timestamp(target)).days) <= 2]
    assert near, "spike near day 120 not found"
    cands = near[0]["candidates"]
    assert cands and cands[0]["factor"] == "Lead"          # leader ranked #1
    assert cands[0]["lag"] >= 1                              # it led the spike
    # attribution rows were persisted
    assert con.execute("SELECT count(*) FROM attributions").fetchone()[0] >= 1
    con.close()
