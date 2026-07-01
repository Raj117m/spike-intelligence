"""Smoke tests for the starter scaffold (Prompts 0-1)."""
from demand.ingest.synthetic import SyntheticSource
from demand.store.schema import connect, init_db, table_counts


def test_schema_creates_all_tables(tmp_path):
    con = connect(tmp_path / "t.duckdb")
    names = init_db(con)
    assert len(names) == 8
    counts = table_counts(con)
    assert set(counts) == set(names)
    # every fact table carries the segment dimension
    cols = {r[1] for r in con.execute("PRAGMA table_info('observations')").fetchall()}
    assert "segment" in cols
    fcols = {r[1] for r in con.execute("PRAGMA table_info('factors')").fetchall()}
    assert "channel" in fcols and "segment" in fcols
    con.close()


def test_synthetic_is_deterministic_and_has_ground_truth():
    a = SyntheticSource(n_products=40, seed=7).fetch()
    b = SyntheticSource(n_products=40, seed=7).fetch()
    # deterministic
    assert a["observations"].equals(b["observations"])
    # ground truth exists and references real (non-decoy) factors
    gt = a["_ground_truth"]
    assert len(gt) > 0
    assert not gt["factor_id"].str.startswith("decoy").any()
    # decoy factors are present in the factor stream (noise the attributor must reject)
    assert a["factors"]["factor_id"].str.startswith("decoy").any()


def test_synthetic_loads_into_store(tmp_path):
    con = connect(tmp_path / "t.duckdb")
    init_db(con)
    data = SyntheticSource(n_products=50, seed=1).fetch()
    for tbl in ("observations", "factors", "_ground_truth"):
        con.register("incoming", data[tbl])
        con.execute(f"INSERT INTO {tbl} SELECT * FROM incoming")
        con.unregister("incoming")
    assert table_counts(con)["observations"] == 50 * 180
    con.close()
