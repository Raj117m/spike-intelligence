"""Offline tests for the permanent pageview store and the DB-backed fetch_series.

The three core guarantees under test:
  1. A first fetch hits the network (_fetch_range called) and saves data to the DB.
  2. A second fetch for the same range skips the network entirely (DB full hit).
  3. A partial hit fetches ONLY the missing tail, not the full range.

load_stored / save_rows are also tested as unit-level contracts.
"""
from datetime import date, timedelta

import duckdb
import pytest

import demand.ingest.wikipedia as wp
from demand.store.pageview_store import ensure_table, load_stored, save_rows
from demand.store.schema import connect

# Fixed anchor for store-unit tests (not today-relative; keeps tests deterministic).
_ANCHOR = date(2024, 1, 1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_con(tmp_path):
    con = connect(tmp_path / "test.duckdb")
    ensure_table(con)
    return con


def _obs_rows(article, start, n):
    """Synthetic OBS_COLS tuples (what _fetch_range returns)."""
    return [
        (article, "ALL", "wiki_pageviews", "wikipedia",
         start + timedelta(days=i), float(1000 + i))
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# load_stored / save_rows unit tests
# ---------------------------------------------------------------------------

def test_load_stored_on_empty_db(tmp_path):
    """Empty DB returns an empty DataFrame with the correct columns."""
    con = _make_con(tmp_path)
    df = load_stored("Demo", _ANCHOR, _ANCHOR + timedelta(days=10), con)
    assert df.empty
    assert list(df.columns) == ["ts", "value"]
    con.close()


def test_save_and_load_roundtrip(tmp_path):
    """Saved rows are retrieved intact and in date order."""
    con = _make_con(tmp_path)
    rows = [(_ANCHOR + timedelta(days=i), float(100 + i)) for i in range(5)]
    n = save_rows("Demo", rows, con)
    assert n == 5
    df = load_stored("Demo", _ANCHOR, _ANCHOR + timedelta(days=4), con)
    assert len(df) == 5
    assert list(df["value"]) == [100.0, 101.0, 102.0, 103.0, 104.0]
    con.close()


def test_save_rows_deduplication(tmp_path):
    """Inserting the same rows a second time inserts nothing and leaves no duplicates."""
    con = _make_con(tmp_path)
    rows = [(_ANCHOR + timedelta(days=i), float(i)) for i in range(3)]
    save_rows("Demo", rows, con)
    n = save_rows("Demo", rows, con)
    assert n == 0
    df = load_stored("Demo", _ANCHOR, _ANCHOR + timedelta(days=2), con)
    assert len(df) == 3
    con.close()


def test_save_rows_partial_overlap(tmp_path):
    """Overlapping insert saves only the truly new dates."""
    con = _make_con(tmp_path)
    rows_a = [(_ANCHOR + timedelta(days=i), float(i)) for i in range(3)]       # days 0-2
    rows_b = [(_ANCHOR + timedelta(days=i), float(i)) for i in range(1, 5)]    # days 1-4
    save_rows("Demo", rows_a, con)
    n = save_rows("Demo", rows_b, con)
    assert n == 2   # days 3 and 4 are new
    df = load_stored("Demo", _ANCHOR, _ANCHOR + timedelta(days=4), con)
    assert len(df) == 5
    con.close()


# ---------------------------------------------------------------------------
# fetch_series integration tests
# ---------------------------------------------------------------------------

def test_fetch_series_first_call_hits_network_and_saves(monkeypatch, tmp_path):
    """First call: DB is empty → _fetch_range is called; data is saved to the DB."""
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=29)   # fetch_series(days=29) needs [today-31, today-2]

    con = connect(tmp_path / "test.duckdb")
    fake_rows = _obs_rows("Demo", start, 30)
    calls = []

    def fake_fetch_range(art, fs, fe):
        calls.append((art, fs, fe))
        return [r for r in fake_rows if fs <= r[4] <= fe]

    monkeypatch.setattr(wp, "_fetch_range", fake_fetch_range)

    result = wp.fetch_series("Demo", days=29, _con=con)

    assert len(calls) == 1, "network should be called exactly once on a cold DB"
    assert not result.empty
    assert len(result) == 30

    # data must be persisted so next call can skip the network
    ensure_table(con)
    stored = load_stored("Demo", start, end, con)
    assert len(stored) == 30
    con.close()


def test_fetch_series_second_call_skips_network(monkeypatch, tmp_path):
    """Second call for the same range: DB has all data → _fetch_range not called."""
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=29)

    con = connect(tmp_path / "test.duckdb")
    ensure_table(con)
    rows_to_store = [(start + timedelta(days=i), float(1000 + i)) for i in range(30)]
    save_rows("Demo", rows_to_store, con)

    calls = []
    monkeypatch.setattr(wp, "_fetch_range", lambda *a: calls.append(a) or [])

    result = wp.fetch_series("Demo", days=29, _con=con)

    assert calls == [], "DB had the full range; network must not be called"
    assert len(result) == 30
    con.close()


def test_fetch_series_partial_hit_fetches_only_gap(monkeypatch, tmp_path):
    """DB has the older portion; only the recent missing tail is fetched from the API."""
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=29)
    gap_start = end - timedelta(days=4)   # first day missing from the DB

    con = connect(tmp_path / "test.duckdb")
    ensure_table(con)
    # Store [start, gap_start-1] — the older block
    old_rows = [(start + timedelta(days=i), float(1000 + i))
                for i in range((gap_start - start).days)]
    save_rows("Demo", old_rows, con)

    fetched_ranges = []

    def fake_fetch_range(art, fs, fe):
        fetched_ranges.append((fs, fe))
        return [
            ("Demo", "ALL", "wiki_pageviews", "wikipedia",
             fs + timedelta(days=i), float(2000 + i))
            for i in range((fe - fs).days + 1)
        ]

    monkeypatch.setattr(wp, "_fetch_range", fake_fetch_range)

    result = wp.fetch_series("Demo", days=29, _con=con)

    assert len(fetched_ranges) == 1, "should make exactly one targeted API call"
    fs, fe = fetched_ranges[0]
    assert fs == gap_start, f"expected fetch to start at {gap_start}, got {fs}"
    assert fe == end,       f"expected fetch to end at {end}, got {fe}"
    assert len(result) == 30, "result should combine DB data with the fresh gap"
    con.close()
