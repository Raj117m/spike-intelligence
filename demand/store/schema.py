"""DuckDB schema. Every fact table carries `segment` (and factors carry `channel`)
so the broader demand-OS queries are a GROUP BY, not a rebuild. Attributions are a
first-class table: they are persisted, never thrown away after a prediction."""
from __future__ import annotations

from pathlib import Path

import duckdb

from ..config import settings

# Order matters only for readability; INSERTs below are column-explicit.
TABLES: dict[str, str] = {
    "observations": """
        CREATE TABLE IF NOT EXISTS observations (
            product_id TEXT, segment TEXT, metric TEXT, source TEXT,
            ts DATE, value DOUBLE
        )""",
    "factors": """
        CREATE TABLE IF NOT EXISTS factors (
            factor_id TEXT, category TEXT, channel TEXT, segment TEXT,
            source TEXT, ts DATE, value DOUBLE
        )""",
    "spikes": """
        CREATE TABLE IF NOT EXISTS spikes (
            spike_id TEXT, product_id TEXT, segment TEXT, onset_ts DATE,
            severity DOUBLE, magnitude DOUBLE, persistence INTEGER,
            acceleration DOUBLE, detector_version TEXT
        )""",
    "attributions": """
        CREATE TABLE IF NOT EXISTS attributions (
            spike_id TEXT, factor_id TEXT, effect_size DOUBLE,
            posterior_incl_prob DOUBLE, lag_days INTEGER,
            model_version TEXT, run_ts TIMESTAMP
        )""",
    "signatures": """
        CREATE TABLE IF NOT EXISTS signatures (
            signature_id TEXT, factor_set TEXT, category_scope TEXT,
            lag_dist TEXT, hit_rate DOUBLE, support_n INTEGER
        )""",
    "predictions": """
        CREATE TABLE IF NOT EXISTS predictions (
            pred_id TEXT, product_id TEXT, segment TEXT, made_ts TIMESTAMP,
            window_start DATE, window_end DATE, prob DOUBLE,
            signature_id TEXT, status TEXT
        )""",
    "outcomes": """
        CREATE TABLE IF NOT EXISTS outcomes (
            pred_id TEXT, realized BOOLEAN, realized_ts TIMESTAMP, error DOUBLE
        )""",
    # hidden ground-truth for validating the detector/attributor on synthetic data
    "_ground_truth": """
        CREATE TABLE IF NOT EXISTS _ground_truth (
            product_id TEXT, segment TEXT, onset_ts DATE,
            factor_id TEXT, lag_days INTEGER
        )""",
    "categories": """
        CREATE TABLE IF NOT EXISTS categories (
            category_id TEXT,
            name TEXT,
            source TEXT,
            created_ts TIMESTAMP
        )""",

    "category_relationships": """
        CREATE TABLE IF NOT EXISTS category_relationships (
            parent_category TEXT,
            child_category TEXT,
            relationship TEXT
        )""",

    "product_categories": """
        CREATE TABLE IF NOT EXISTS product_categories (
            product_id TEXT,
            category_id TEXT,
            confidence DOUBLE,
            source TEXT
        )""",

    "factor_categories": """
        CREATE TABLE IF NOT EXISTS factor_categories (
            factor_id TEXT,
            category_id TEXT,
            confidence DOUBLE,
            source TEXT
        )""",
}


def connect(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    p = Path(db_path or settings.db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(p))


def init_db(con: duckdb.DuckDBPyConnection) -> list[str]:
    for ddl in TABLES.values():
        con.execute(ddl)
    return list(TABLES)


def table_counts(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in TABLES:
        counts[name] = con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
    return counts
