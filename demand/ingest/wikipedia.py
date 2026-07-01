"""Real, free data connector: Wikipedia daily pageviews.

Pageviews are a public *attention / demand proxy* - no API key, no payment, no extra
libraries (uses Python's built-in urllib). We pull real daily interest for real topics
and feed it into the same `observations` table the synthetic data used, so the exact
same detector runs on real data.

API: https://wikimedia.org/api/rest_v1/  (Wikimedia REST, public)
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

import pandas as pd

from .base import Source

API = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
       "en.wikipedia/all-access/all-agents/{article}/daily/{start}/{end}")

# Wikimedia requires a descriptive User-Agent or it returns 403.
UA = "SpikeIntelligence/0.1 (learning project)"

# Disk cache: responses are keyed by URL hash and expire after 24 h.
_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "spike-intelligence", "wikimedia")
_CACHE_TTL = 86_400  # seconds (1 day)

# Seconds to wait before each successive retry on HTTP 429.
_RETRY_DELAYS = (1, 2, 4)

# Safe, definitely-existing default articles with real attention dynamics.
DEFAULT_ARTICLES = [
    "PlayStation_5", "IPhone_16", "Barbie_(film)",
    "Oppenheimer_(film)", "ChatGPT", "Taylor_Swift",
]

OBS_COLS = ["product_id", "segment", "metric", "source", "ts", "value"]

WP_API = "https://en.wikipedia.org/w/api.php"
TOP_API = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
           "en.wikipedia/all-access/{y}/{m}/{d}")

# Non-article pages to drop from the trending firehose.
SKIP_PREFIXES = ("Special:", "Wikipedia:", "Portal:", "Help:", "Category:",
                 "Template:", "File:", "Talk:", "Draft:", "User:")


def _cache_path(url: str) -> str:
    key = hashlib.sha256(url.encode()).hexdigest()
    return os.path.join(_CACHE_DIR, key + ".json")


def _get_json(url: str) -> dict:
    """Single chokepoint for GET-JSON with disk cache and retry-on-429.

    Cache: responses are stored by URL hash under _CACHE_DIR and served from
    disk if younger than _CACHE_TTL seconds (1 day by default).

    Retry: HTTP 429 (rate-limit) is retried up to len(_RETRY_DELAYS) times
    with the configured waits between attempts; any other HTTP error propagates
    immediately.
    """
    path = _cache_path(url)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < _CACHE_TTL:
        with open(path) as fh:
            return json.load(fh)

    last_exc: Exception | None = None
    for wait in (0, *_RETRY_DELAYS):
        if wait:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as fh:
                json.dump(data, fh)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                last_exc = exc
                continue
            raise
    assert last_exc is not None
    raise last_exc


def resolve_title(query: str) -> str | None:
    """Turn loose free text into the best REAL Wikipedia title (or None). Fixes the
    'must type the exact title' problem - this is the reliability fix."""
    try:
        qs = urllib.parse.urlencode({"action": "query", "list": "search",
                                     "srsearch": query, "srlimit": 1, "format": "json"})
        data = _get_json(f"{WP_API}?{qs}")
        hits = data.get("query", {}).get("search", [])
        return hits[0]["title"] if hits else None
    except Exception:  # noqa: BLE001
        return None


def related_titles(title: str, limit: int = 6) -> list[str]:
    """Auto-discover related topics (environmental factors) via search 'morelike'."""
    try:
        qs = urllib.parse.urlencode({"action": "query", "list": "search",
                                     "srsearch": f"morelike:{title}", "srlimit": limit,
                                     "format": "json", "srprop": ""})
        data = _get_json(f"{WP_API}?{qs}")
        return [h["title"] for h in data.get("query", {}).get("search", [])][:limit]
    except Exception:  # noqa: BLE001
        return []


def top_articles(limit: int = 20, days_ago: int = 2) -> list[tuple[str, int]]:
    """Free 'firehose': the most-viewed real articles on a recent day = what is
    spiking in attention right now. Returns [(article, views), ...]."""
    d = date.today() - timedelta(days=days_ago)
    url = TOP_API.format(y=d.strftime("%Y"), m=d.strftime("%m"), d=d.strftime("%d"))
    try:
        data = _get_json(url)
        arts = data.get("items", [{}])[0].get("articles", [])
    except Exception:  # noqa: BLE001
        return []
    out: list[tuple[str, int]] = []
    for a in arts:
        name = a.get("article", "")
        if not name or name in ("Main_Page", "-") or name.startswith(SKIP_PREFIXES):
            continue
        out.append((name, int(a.get("views", 0))))
        if len(out) >= limit:
            break
    return out


def parse_items(article: str, payload: dict) -> list[tuple]:
    """Turn a Wikimedia pageviews JSON payload into observation rows. Pure (testable)."""
    rows = []
    for it in payload.get("items", []):
        stamp = str(it.get("timestamp", ""))[:8]
        if len(stamp) != 8:
            continue
        ts = pd.to_datetime(stamp, format="%Y%m%d").date()
        rows.append((article, "ALL", "wiki_pageviews", "wikipedia", ts, float(it.get("views", 0))))
    return rows


def _fetch_range(article: str, start: date, end: date) -> list[tuple]:
    """Fetch Wikimedia pageviews for [start, end] and return parsed OBS_COLS rows.
    Returns an empty list on any network or parsing failure."""
    url = API.format(
        article=urllib.parse.quote(article, safe=""),
        start=start.strftime("%Y%m%d"),
        end=end.strftime("%Y%m%d"),
    )
    try:
        return parse_items(article, _get_json(url))
    except Exception:  # noqa: BLE001
        return []


def fetch_series(title: str, days: int = 180, _con=None) -> pd.DataFrame:
    """Daily [ts, value] for one Wikipedia title, backed by a permanent local store.

    First reads what is already stored in the project DuckDB ``pageviews`` table for
    this topic; then fetches only the missing date window from Wikimedia and saves it
    permanently.  A repeat call for the same topic and range returns from the database
    without any network round-trip.  Only the most-recent 1-2 days (the API lag) need
    to be fetched on each subsequent run, so API dependence shrinks over time.

    ``_con``: optional existing DuckDB connection (pass in tests to inject a temp DB;
    leave as ``None`` in production to auto-open ``settings.db_path``).
    """
    from ..store.pageview_store import ensure_table, load_stored, save_rows
    from ..store.schema import connect

    article = title.strip().replace(" ", "_")
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=days)

    own_con = _con is None
    con = _con if _con is not None else connect()
    ensure_table(con)
    try:
        local = load_stored(article, start, end, con)
        have = set(local["ts"]) if not local.empty else set()

        needed = {start + timedelta(days=i) for i in range((end - start).days + 1)}
        missing = sorted(needed - have)

        if missing:
            new_rows = _fetch_range(article, missing[0], missing[-1])
            if new_rows:
                save_rows(article, [(r[4], r[5]) for r in new_rows], con)
                new_df = pd.DataFrame(new_rows, columns=OBS_COLS)[["ts", "value"]]
                local = (
                    pd.concat([local, new_df])
                    .drop_duplicates("ts")
                    .sort_values("ts")
                    .reset_index(drop=True)
                    if not local.empty
                    else new_df.sort_values("ts").reset_index(drop=True)
                )

        return local if not local.empty else pd.DataFrame(columns=["ts", "value"])
    finally:
        if own_con:
            con.close()


class WikipediaSource(Source):
    def __init__(self, articles: list[str] | None = None, days: int = 180):
        self.articles = articles or list(DEFAULT_ARTICLES)
        self.days = days

    def name(self) -> str:
        return "wikipedia"

    def _fetch_one(self, article: str) -> list[tuple]:
        end = date.today() - timedelta(days=2)          # data lags ~1-2 days
        start = end - timedelta(days=self.days)
        url = API.format(
            article=urllib.parse.quote(article, safe=""),
            start=start.strftime("%Y%m%d"),
            end=end.strftime("%Y%m%d"),
        )
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
        return parse_items(article, payload)

    def fetch_series(self, title: str) -> pd.DataFrame:
        """Daily [ts, value] for one title. Empty frame on any failure (e.g. 404)."""
        try:
            rows = self._fetch_one(title.strip().replace(" ", "_"))
        except Exception:  # noqa: BLE001
            return pd.DataFrame(columns=["ts", "value"])
        df = pd.DataFrame(rows, columns=OBS_COLS)
        return df[["ts", "value"]] if not df.empty else pd.DataFrame(columns=["ts", "value"])

    def fetch(self) -> dict[str, pd.DataFrame]:
        all_rows: list[tuple] = []
        for a in self.articles:
            try:
                rows = self._fetch_one(a)
                all_rows.extend(rows)
                print(f"  {a}: {len(rows)} days")
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"  {a}: skipped ({exc.__class__.__name__})")
            time.sleep(0.2)  # be polite to the API
        return {"observations": pd.DataFrame(all_rows, columns=OBS_COLS)}
