"""Permanent local store for Wikipedia daily pageview series.

Every series we fetch from Wikimedia is persisted in the ``pageviews`` table of the
project DuckDB database.  On subsequent calls only the missing date window is fetched
from the live API -- so repeat runs lean heavily on local data, and we accumulate
history that Wikipedia's API eventually drops from its retention window.

The ``pageviews`` table is managed here and is separate from the analytics tables
created by ``init_db`` in schema.py.  Call ``ensure_table(con)`` once before any
read or write operation (``fetch_series`` does this automatically).
"""
from __future__ import annotations

from datetime import date

import pandas as pd

_DDL = """
    CREATE TABLE IF NOT EXISTS pageviews (
        topic TEXT,
        ts    DATE,
        views DOUBLE
    )
"""


def ensure_table(con) -> None:
    """Create the pageviews table if it does not already exist.  Safe to call repeatedly."""
    con.execute(_DDL)


def load_stored(topic: str, start: date, end: date, con) -> pd.DataFrame:
    """Return stored [ts, value] rows for *topic* in [start, end] inclusive.

    Returns an empty DataFrame (columns: ts, value) if nothing is stored for that
    topic in the requested range.
    """
    rows = con.execute(
        "SELECT ts, views FROM pageviews "
        "WHERE topic = ? AND ts >= ? AND ts <= ? "
        "ORDER BY ts",
        [topic, start, end],
    ).fetchall()
    if not rows:
        return pd.DataFrame(columns=["ts", "value"])
    df = pd.DataFrame(rows, columns=["ts", "value"])
    df["ts"] = pd.to_datetime(df["ts"]).dt.date
    return df


def save_rows(topic: str, rows: list[tuple[date, float]], con) -> int:
    """Persist (date, views) pairs for *topic*, skipping any dates already stored.

    Returns the number of rows actually inserted (0 when everything was already
    present -- callers can use this to detect a no-op second write).
    """
    if not rows:
        return 0
    min_d = min(r[0] for r in rows)
    max_d = max(r[0] for r in rows)
    existing = {
        r[0]
        for r in con.execute(
            "SELECT ts FROM pageviews WHERE topic = ? AND ts >= ? AND ts <= ?",
            [topic, min_d, max_d],
        ).fetchall()
    }
    new_rows = [(topic, d, v) for d, v in rows if d not in existing]
    if not new_rows:
        return 0
    df = pd.DataFrame(new_rows, columns=["topic", "ts", "views"])
    con.register("_pv_new", df)
    con.execute("INSERT INTO pageviews SELECT * FROM _pv_new")
    con.unregister("_pv_new")
    return len(new_rows)
