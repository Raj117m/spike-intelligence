"""Tests for the real (Wikipedia) connector - parser + detector path, no network."""
import hashlib
import json
from datetime import date, timedelta

import numpy as np
import pandas as pd
import urllib.error
import urllib.request

import demand.ingest.wikipedia as wp
from demand.detect.detector import detect
from demand.ingest.wikipedia import OBS_COLS, parse_items
from demand.store.schema import connect, init_db


def _payload(n=180, spike_at=120):
    """Build a realistic pageviews payload (weekly cycle + noise + one spike)."""
    rng = np.random.default_rng(0)
    items = []
    start = date(2024, 1, 1)
    for i in range(n):
        v = 1000 + 150 * np.sin(2 * np.pi * i / 7) + rng.normal(0, 80)
        if spike_at <= i < spike_at + 3:
            v += 1800 * (1 - (i - spike_at) / 3)
        stamp = (start + timedelta(days=i)).strftime("%Y%m%d") + "00"
        items.append({"timestamp": stamp, "views": int(max(v, 0))})
    return {"items": items}


def test_parse_items_shape():
    rows = parse_items("Demo", _payload(5, 99))
    assert len(rows) == 5
    assert rows[0][0] == "Demo"
    assert rows[0][2] == "wiki_pageviews"
    assert rows[0][3] == "wikipedia"


def test_parse_items_handles_garbage():
    rows = parse_items("Demo", {"items": [{"timestamp": "bad", "views": 5}, {}]})
    assert rows == []


def test_detector_runs_on_wiki_shaped_data(tmp_path):
    con = connect(tmp_path / "w.duckdb")
    init_db(con)
    df = pd.DataFrame(parse_items("Demo", _payload(180, 120)), columns=OBS_COLS)
    con.register("inc", df)
    con.execute("INSERT INTO observations SELECT * FROM inc")
    con.unregister("inc")
    assert detect(con, k=3.0, d=2) >= 1   # finds the planted spike
    con.close()


# ---------------------------------------------------------------------------
# Helpers for cache / retry tests
# ---------------------------------------------------------------------------

class _FakeResp:
    """Minimal file-like context manager that stands in for urlopen's response."""
    def __init__(self, data: dict):
        self._body = json.dumps(data).encode()

    def read(self, n: int = -1) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


def _make_429():
    return urllib.error.HTTPError("http://x", 429, "Too Many Requests", {}, None)


def _url_cache_file(tmp_path, url: str):
    key = hashlib.sha256(url.encode()).hexdigest()
    return tmp_path / (key + ".json")


# ---------------------------------------------------------------------------
# Cache tests
# ---------------------------------------------------------------------------

def test_cache_hit_skips_network(monkeypatch, tmp_path):
    """A fresh cache entry is returned without making a network call."""
    monkeypatch.setattr(wp, "_CACHE_DIR", str(tmp_path))
    url = "http://example.com/cached"
    stored = {"items": [{"ts": "20240101", "views": 42}]}
    _url_cache_file(tmp_path, url).write_text(json.dumps(stored))

    calls = []
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **kw: calls.append(1) or _FakeResp({}))

    result = wp._get_json(url)
    assert result == stored
    assert calls == []  # network never touched


def test_cache_miss_fetches_and_saves(monkeypatch, tmp_path):
    """On a cache miss the response is fetched and written to disk."""
    monkeypatch.setattr(wp, "_CACHE_DIR", str(tmp_path))
    url = "http://example.com/fresh"
    payload = {"items": [{"ok": True}]}
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **kw: _FakeResp(payload))

    result = wp._get_json(url)
    assert result == payload

    cache_file = _url_cache_file(tmp_path, url)
    assert cache_file.exists()
    assert json.loads(cache_file.read_text()) == payload


def test_second_call_served_from_cache(monkeypatch, tmp_path):
    """After a fetch the second call is served from disk, not the network."""
    monkeypatch.setattr(wp, "_CACHE_DIR", str(tmp_path))
    url = "http://example.com/second"
    payload = {"items": []}
    call_count = []
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **kw: call_count.append(1) or _FakeResp(payload))

    wp._get_json(url)
    wp._get_json(url)
    assert len(call_count) == 1  # second call came from cache


# ---------------------------------------------------------------------------
# Retry tests
# ---------------------------------------------------------------------------

def test_retry_on_429_eventually_succeeds(monkeypatch, tmp_path):
    """Two 429 responses followed by success → returns data after 3 attempts."""
    monkeypatch.setattr(wp, "_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(wp, "_RETRY_DELAYS", (0, 0))  # no sleeping in tests
    url = "http://example.com/rate-limited"
    payload = {"items": [{"ok": True}]}
    calls = []

    def fake_urlopen(*a, **kw):
        calls.append(1)
        if len(calls) <= 2:
            raise _make_429()
        return _FakeResp(payload)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = wp._get_json(url)
    assert result == payload
    assert len(calls) == 3


def test_retry_exhausted_raises_429(monkeypatch, tmp_path):
    """When all retries are spent a 429 HTTPError propagates to the caller."""
    monkeypatch.setattr(wp, "_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(wp, "_RETRY_DELAYS", (0, 0))

    def always_429(*a, **kw):
        raise _make_429()

    monkeypatch.setattr(urllib.request, "urlopen", always_429)

    import pytest
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        wp._get_json("http://example.com/always-429")
    assert exc_info.value.code == 429


def test_non_429_http_error_not_retried(monkeypatch, tmp_path):
    """A non-rate-limit HTTP error (e.g. 404) is raised immediately, no retries."""
    monkeypatch.setattr(wp, "_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(wp, "_RETRY_DELAYS", (0, 0))
    calls = []

    def fake_404(*a, **kw):
        calls.append(1)
        raise urllib.error.HTTPError("http://x", 404, "Not Found", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", fake_404)

    import pytest
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        wp._get_json("http://example.com/missing")
    assert exc_info.value.code == 404
    assert len(calls) == 1  # no retries for 404
