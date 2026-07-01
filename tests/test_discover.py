"""Tests for the reliability + discovery layer (resolver, related, firehose).
Network is monkeypatched via the single _get_json chokepoint."""
import demand.ingest.wikipedia as wp


def test_resolve_title_picks_top_hit(monkeypatch):
    monkeypatch.setattr(wp, "_get_json", lambda url: {
        "query": {"search": [{"title": "Stanley (brand)"}, {"title": "Other"}]}})
    assert wp.resolve_title("stanley tumbler") == "Stanley (brand)"


def test_resolve_title_none_on_no_hits(monkeypatch):
    monkeypatch.setattr(wp, "_get_json", lambda url: {"query": {"search": []}})
    assert wp.resolve_title("zzzzz nonsense qqq") is None


def test_resolve_title_survives_network_error(monkeypatch):
    def boom(url):
        raise OSError("network down")
    monkeypatch.setattr(wp, "_get_json", boom)
    assert wp.resolve_title("anything") is None


def test_related_titles(monkeypatch):
    monkeypatch.setattr(wp, "_get_json", lambda url: {
        "query": {"search": [{"title": "Pop Mart"}, {"title": "Blind box"}]}})
    assert wp.related_titles("Labubu") == ["Pop Mart", "Blind box"]


def test_top_articles_filters_non_articles(monkeypatch):
    monkeypatch.setattr(wp, "_get_json", lambda url: {"items": [{"articles": [
        {"article": "Main_Page", "views": 9999999, "rank": 1},
        {"article": "Special:Search", "views": 888888, "rank": 2},
        {"article": "Labubu", "views": 120000, "rank": 3},
        {"article": "PlayStation_5", "views": 90000, "rank": 4},
    ]}]})
    out = wp.top_articles(limit=10)
    names = [n for n, _ in out]
    assert "Main_Page" not in names and "Special:Search" not in names
    assert names == ["Labubu", "PlayStation_5"]
    assert out[0] == ("Labubu", 120000)
