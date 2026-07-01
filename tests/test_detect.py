"""Prompt 2 detector smoke test: it should recover a good share of known spikes."""
from demand.detect.detector import detect, score
from demand.ingest.synthetic import SyntheticSource
from demand.store.schema import connect, init_db


def test_detector_recovers_known_spikes(tmp_path):
    con = connect(tmp_path / "d.duckdb")
    init_db(con)
    data = SyntheticSource(n_products=120, seed=3).fetch()
    for t in ("observations", "factors", "_ground_truth"):
        con.register("inc", data[t])
        con.execute(f"INSERT INTO {t} SELECT * FROM inc")
        con.unregister("inc")

    n = detect(con, k=3.0, d=2)
    assert n > 0

    m = score(con, tol=2)
    # loose, stable thresholds (real numbers run ~0.8)
    assert m["precision"] >= 0.5
    assert m["recall"] >= 0.5
    con.close()
