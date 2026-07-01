"""Command line interface.

  demand init                         create the database + 8 tables
  demand synth --products 500 --seed 1   generate synthetic ground-truth data
  demand info                         show row counts + a few injected spikes

Run via:  uv run demand <command>
"""
from __future__ import annotations

import typer

from .config import settings
from .ingest.synthetic import SyntheticSource
from .store.schema import connect, init_db, table_counts

app = typer.Typer(add_completion=False, help="Spike Intelligence CLI (starter)")

SYNTH_TABLES = ("observations", "factors", "_ground_truth")


@app.command()
def init() -> None:
    """Create the DuckDB database and all tables."""
    con = connect()
    names = init_db(con)
    con.close()
    typer.echo(f"Initialized {settings.db_path} with {len(names)} tables: {', '.join(names)}")


@app.command()
def synth(products: int = 500, days: int = 180, seed: int = 1) -> None:
    """Generate a synthetic universe with known spikes and known causes."""
    con = connect()
    init_db(con)
    for tbl in SYNTH_TABLES:
        con.execute(f"DELETE FROM {tbl}")
    data = SyntheticSource(n_products=products, days=days, seed=seed).fetch()
    for tbl in SYNTH_TABLES:
        con.register("incoming", data[tbl])
        con.execute(f"INSERT INTO {tbl} SELECT * FROM incoming")
        con.unregister("incoming")
    counts = table_counts(con)
    con.close()
    typer.echo(
        f"Generated {products} products over {days} days (seed={seed}). "
        f"observations={counts['observations']:,}  factors={counts['factors']:,}  "
        f"injected_spikes={counts['_ground_truth']:,}"
    )


@app.command()
def info() -> None:
    """Show table row counts and a sample of injected (ground-truth) spikes."""
    con = connect()
    init_db(con)
    counts = table_counts(con)
    typer.echo("Row counts:")
    for name, n in counts.items():
        typer.echo(f"  {name:<14} {n:>10,}")

    n_gt = counts["_ground_truth"]
    if n_gt:
        typer.echo("\nSample injected spikes (product -> cause @ onset, lag):")
        rows = con.execute(
            "SELECT product_id, factor_id, onset_ts, lag_days "
            "FROM _ground_truth ORDER BY product_id LIMIT 8"
        ).fetchall()
        for pid, fid, onset, lag in rows:
            typer.echo(f"  {pid}  <-  {fid:<18} @ {onset}  (lag {lag}d)")
        typer.echo("\nMost common demand drivers (ground truth):")
        drivers = con.execute(
            "SELECT factor_id, count(*) AS n FROM _ground_truth "
            "GROUP BY factor_id ORDER BY n DESC"
        ).fetchall()
        for fid, n in drivers:
            typer.echo(f"  {fid:<18} {n:>6}")
    else:
        typer.echo("\nNo data yet - run:  uv run demand synth")
    con.close()


@app.command()
def detect(
    k: float = typer.Option(3.0, help="robust z threshold"),
    d: int = typer.Option(2, help="minimum sustained days"),
) -> None:
    """Detect spikes (STL + robust z + accel) and write the `spikes` table."""
    from .detect.detector import detect as run_detect

    n = run_detect(k=k, d=d)
    typer.echo(f"Detected {n} spikes (k={k}, d={d}) -> written to `spikes`.")


@app.command("score-detect")
def score_detect(tol: int = typer.Option(2, help="match window in days")) -> None:
    """Score detected spikes against the known (synthetic) ground truth."""
    from .detect.detector import score

    m = score(tol=tol)
    typer.echo("Detection vs ground truth:")
    typer.echo(f"  detected={m['detected']}  ground_truth={m['ground_truth']}  "
               f"true_positives={m['true_positives']}")
    typer.echo(f"  precision={m['precision']:.2f}  recall={m['recall']:.2f}  "
               f"F1={m['f1']:.2f}")


@app.command("pull-wiki")
def pull_wiki(
    articles: str = typer.Option("", help="comma-separated Wikipedia titles; blank = a default set"),
    days: int = typer.Option(180, help="how many days of history to pull"),
) -> None:
    """Pull REAL daily Wikipedia pageviews, then run the detector on them."""
    from .detect.detector import detect
    from .ingest.wikipedia import DEFAULT_ARTICLES, WikipediaSource

    arts = [a.strip().replace(" ", "_") for a in articles.split(",") if a.strip()] or DEFAULT_ARTICLES
    con = connect()
    init_db(con)
    typer.echo(f"Pulling real Wikipedia pageviews for {len(arts)} topics (last {days} days):")
    obs = WikipediaSource(articles=arts, days=days).fetch()["observations"]
    if obs.empty:
        typer.echo("No data returned - check the article titles (they must match Wikipedia exactly).")
        raise typer.Exit(1)

    # switch the project into REAL-DATA mode (clear synthetic-only tables)
    for tbl in ("observations", "factors", "_ground_truth", "spikes"):
        con.execute(f"DELETE FROM {tbl}")
    con.register("inc", obs)
    con.execute("INSERT INTO observations SELECT * FROM inc")
    con.unregister("inc")
    typer.echo(f"Loaded {len(obs):,} real daily observations across "
               f"{obs['product_id'].nunique()} topics.")

    n = detect(con)
    typer.echo(f"Detector found {n} spike(s) in the real data.")
    rows = con.execute(
        "SELECT product_id, onset_ts, round(magnitude, 1) "
        "FROM spikes ORDER BY magnitude DESC LIMIT 12"
    ).fetchall()
    if rows:
        typer.echo("\nTop real attention spikes (topic @ date, strength in 'wobbles'):")
        for pid, onset, mag in rows:
            typer.echo(f"  {pid:<22} {onset}   z={mag}")
    typer.echo("\n(To go back to practice data later, run:  uv run demand synth)")
    con.close()


@app.command()
def explain(
    product: str = typer.Option("ChatGPT", help="product/topic name (loose text is fine)"),
    factors: str = typer.Option("", help="comma-separated factor topics; blank = auto-discover"),
    days: int = typer.Option(180, help="days of history"),
) -> None:
    """Pull REAL attention for a product + its environmental factors, find its spikes,
    and rank which factor most likely caused each one. Loose names are auto-resolved."""
    from .attribute.attributor import explain as run_explain

    fts = [x for x in factors.split(",") if x.strip()]
    typer.echo(f"Analyzing '{product}' (last {days} days)...")
    r = run_explain(product, fts, days=days)
    if "error" in r:
        typer.echo(r["error"])
        raise typer.Exit(1)

    if r["product_input"].strip().replace(" ", "_") != r["product"]:
        typer.echo(f"Resolved '{r['product_input']}' -> {r['product'].replace('_', ' ')}")
    label = "Auto-discovered factors" if r["auto_factors"] else "Factors"
    typer.echo(f"{label}: {', '.join(x.replace('_', ' ') for x in r['loaded']) or 'none'}"
               + (f"   (skipped: {', '.join(r['skipped'])})" if r["skipped"] else ""))

    if not r["spikes"]:
        typer.echo("\nNo spikes detected in this product's attention in this window.")
    for sp in r["spikes"]:
        typer.echo(f"\nSPIKE on {sp['onset']}  (strength z={sp['magnitude']:.1f})")
        if sp["candidates"]:
            for c in sp["candidates"][:4]:
                typer.echo(f"   reason: {c['factor']:<24} rose z={c['effect']:.1f}, "
                           f"{c['lag']}d earlier   (share {c['prob'] * 100:.0f}%)")
        else:
            typer.echo("   no leading environmental factor found (try different factors)")

    if r["live"]:
        typer.echo("\nLIVE SIGNALS (factor rising in the last 5 days -> possible upcoming spike):")
        for live in r["live"]:
            typer.echo(f"   {live['factor']:<24} z={live['z']:.1f} now")

    typer.echo("\nNote: attribution here is leading-indicator (correlation + timing), not proof.")


@app.command()
def discover(limit: int = typer.Option(20, help="how many trending topics to show")) -> None:
    """Free firehose: the most-viewed Wikipedia topics on a recent day = what is
    spiking in attention right now. Pick any and run `explain` on it."""
    from .ingest.wikipedia import top_articles

    rows = top_articles(limit=limit)
    if not rows:
        typer.echo("Couldn't fetch the trending list (check your internet and try again).")
        raise typer.Exit(1)
    typer.echo("Biggest attention right now on Wikipedia (free, live):\n")
    for i, (name, views) in enumerate(rows, 1):
        typer.echo(f"  {i:>2}. {name.replace('_', ' '):<34} {views:>10,} views")
    typer.echo('\nAnalyze any of these:  uv run demand explain --product "<name>"')


@app.command()
def watch(
    limit: int = typer.Option(10, help="how many trending topics to scan"),
    days: int = typer.Option(120, help="history per topic"),
    recent: int = typer.Option(28, help="a spike must be within this many days to count as 'now'"),
) -> None:
    """LIVE WATCHLIST: scan trending topics and, for each one spiking now, show the
    environmental factor most likely driving it. Fully automatic - names nothing."""
    from .attribute.attributor import watch as run_watch

    typer.echo("Scanning what's spiking right now and why (live APIs, ~30-60s)...")
    r = run_watch(limit=limit, days=days, recent_days=recent)
    board = r["board"]
    if not board:
        typer.echo(f"\nScanned {r['scanned']} trending topics; none had a fresh spike "
                   f"in the last {recent} days.")
        return
    typer.echo(f"\nLIVE WATCHLIST - {len(board)} topic(s) spiking in the last {recent} "
               f"days (of {r['scanned']} scanned):\n")
    for b in board:
        reason = b["reason"]
        rtxt = (f"{reason['factor'].replace('_', ' ')}  (z={reason['effect']:.1f}, "
                f"{reason['lag']}d earlier)" if reason else "no clear factor found")
        typer.echo(f"  {b['topic'].replace('_', ' '):<26} spike {b['onset']}  "
                   f"(z={b['magnitude']:.1f})")
        typer.echo(f"       -> likely driver: {rtxt}")
    typer.echo("\nNote: leading-indicator association, not proof. All free Wikimedia data.")


@app.command()
def backtest(
    product: str = typer.Option("ChatGPT", help="product/topic (loose text is fine)"),
    factors: str = typer.Option("", help="comma-separated factors; blank = auto-discover"),
    days: int = typer.Option(365, help="history to test over"),
    lead: int = typer.Option(10, help="a signal predicts a spike within this many days"),
    threshold: float = typer.Option(3.0, help="how high a factor must rise to fire a signal"),
) -> None:
    """Does a rising factor actually PREDICT the spike? Measure precision, recall, lead
    time, and lift over chance on real history."""
    from .evaluate.backtest import backtest as run_bt

    fts = [x for x in factors.split(",") if x.strip()]
    typer.echo(f"Backtesting '{product}' over ~{days} days "
               f"(signal = a factor rising; predict a spike within {lead} days)...")
    r = run_bt(product, fts, days=days, lead=lead, threshold=threshold)
    if "error" in r:
        typer.echo(r["error"])
        raise typer.Exit(1)

    typer.echo(f"Factors: {', '.join(x.replace('_', ' ') for x in r['loaded']) or 'none'}")
    typer.echo(f"\nHistory: {r['n_days']} days | {r['n_spikes']} spikes | "
               f"{r['n_signals']} factor signals")
    typer.echo(f"  Precision:        {r['precision'] * 100:>4.0f}%   (signals followed by a spike)")
    typer.echo(f"  Recall:           {r['recall'] * 100:>4.0f}%   (spikes that had a leading signal)")
    typer.echo(f"  Median lead time: {r['median_lead']:>4.0f} days")
    typer.echo(f"  Base rate (chance): {r['base_rate'] * 100:>3.0f}%")
    lift = r["lift"]
    typer.echo(f"  LIFT over chance:  {('%.1fx' % lift) if lift is not None else 'n/a'}")

    if lift is None or r["n_signals"] < 3:
        verdict = "too few signals/spikes to judge - widen the window or add factors."
    elif lift >= 1.5:
        verdict = "the rising-factor signal carries REAL predictive information."
    elif lift >= 1.1:
        verdict = "weak signal - a little better than chance, not much."
    else:
        verdict = "no better than chance for this product / these factors."
    typer.echo(f"\nVerdict: {verdict}")
    typer.echo("Caveat: predictive association on attention data, not proof of causation.")


@app.command()
def radar(
    limit: int = typer.Option(8, help="how many trending topics to scan"),
    lead: int = typer.Option(10, help="prediction window in days"),
    days: int = typer.Option(365, help="history per topic for confidence scoring"),
) -> None:
    """THE ONE COMMAND: scan what's trending, find forward opportunities (a historically
    reliable factor rising now), grade past calls, and save a dated report."""
    from .radar import radar as run_radar

    typer.echo("Running the opportunity radar (live APIs, ~1-2 min)...")
    r = run_radar(limit=limit, lead=lead, days=days)

    t = r["track"]
    if t["rate"] is not None:
        typer.echo(f"\nTrack record so far: {t['hits']}/{t['scored']} past calls came "
                   f"true ({t['rate'] * 100:.0f}%).")
    else:
        typer.echo("\nTrack record so far: not enough matured predictions yet "
                   "(it builds as you run this over days).")

    typer.echo(f"\n=== FORWARD OPPORTUNITIES (a factor rising now; ~{r['lead']}-day horizon) ===")
    if r["opportunities"]:
        for o in r["opportunities"]:
            lift = f"{o['lift']:.1f}x lift" if o["lift"] is not None else "lift n/a"
            flag = "PROVEN" if o["confidence"] == "proven" else "unproven"
            typer.echo(f"  [{flag:^8}] {o['topic'].replace('_', ' '):<24} "
                       f"<- {o['rising_factor'].replace('_', ' '):<22} rising (z={o['rising_z']:.1f}, {lift})")
    else:
        typer.echo("  none right now.")

    typer.echo("\n=== RECENTLY SPIKED (what just moved) ===")
    for x in r["recent"][:8]:
        drv = x["driver"]["factor"].replace("_", " ") if x["driver"] else "no clear factor"
        typer.echo(f"  {x['topic'].replace('_', ' '):<24} spiked {x['onset']} "
                   f"(z={x['strength']:.1f}) <- {drv}")

    typer.echo(f"\nReport saved: {r['report_path']}")
    typer.echo("Honest note: leads, not guarantees. Acting on one is real-world & risky - start small.")


@app.command()
def forecast(
    limit: int = typer.Option(10, help="how many trending topics to scan"),
    days: int = typer.Option(365, help="days of history for backtesting related-topic signals"),
    lead: int = typer.Option(10, help="max days from factor rise to expected product spike"),
    min_z: float = typer.Option(1.5, help="minimum trailing-z for a factor to count as rising now"),
    min_lift: float = typer.Option(1.2, help="minimum historical lift; drivers below this threshold are ignored"),
) -> None:
    """EARLY-WARNING: products NOT yet spiking, but a related topic rising now has
    historically led their spikes. Only drivers with lift >= min_lift are counted.
    Ranked by early score = sum(rise × lift) over qualifying drivers."""
    from .forecast import forecast as run_forecast

    typer.echo("Scanning for early-warning signals (live APIs, ~30-120s)...")
    results = run_forecast(limit=limit, days=days, lead=lead, min_z=min_z, min_lift=min_lift)

    typer.echo("\n=== EARLY-WARNING FORECAST ===")
    typer.echo("Products NOT yet spiking, but a related topic IS rising now")
    typer.echo("and has historically preceded their spikes. Ranked by signal strength.\n")

    if not results:
        typer.echo("  No early-warning signals detected right now - check back tomorrow.")
        return

    for o in results:
        lift_str = f"{o['best_driver_lift']:.1f}x lift" if o["best_driver_lift"] is not None else "lift n/a"
        lead_str = f"~{o['expected_lead_days']:.0f}d lead" if o["expected_lead_days"] else "lead n/a"
        typer.echo(
            f"  [score {o['early_score']:>6.1f}]  "
            f"{o['product'].replace('_', ' '):<26} "
            f"<- {o['best_driver'].replace('_', ' '):<22} "
            f"(rising z={o['best_driver_z']:.1f}, {lift_str}, {lead_str})"
        )

    typer.echo(f"\n{len(results)} early signal(s) found.")
    typer.echo("Honest note: rising-attention correlation only - not a profit guarantee. "
               "All free Wikimedia data. Start small.")


@app.command("backtest-forecast")
def backtest_forecast_cmd(
    limit: int = typer.Option(20, help="how many trending topics to scan"),
    days: int = typer.Option(365, help="days of history to backtest over"),
    lead: int = typer.Option(10, help="spike-prediction window in days"),
    min_lift: float = typer.Option(1.2, help="minimum historical lift for a driver to qualify"),
) -> None:
    """Does the early-warning strategy buy real lead time? For each trending product,
    find related drivers that pass the lift gate, combine them, and measure precision,
    recall, and median lead time across all products. States plainly whether the
    signals beat chance and arrive ahead of spikes."""
    from .forecast import backtest_forecast as run_bt

    typer.echo(
        f"Backtesting forecast strategy across up to {limit} trending products "
        f"(live APIs, ~1-3 min)..."
    )
    r = run_bt(limit=limit, days=days, lead=lead, min_lift=min_lift)

    typer.echo("\n=== FORECAST BACKTEST RESULTS ===")
    typer.echo(f"Products scanned:                  {r['n_products']}")
    typer.echo(f"Products with qualifying drivers:  {r['n_qualifying']}")

    if not r["per_product"]:
        typer.echo(
            "\nNo products had qualifying drivers — "
            "try a lower --min-lift or a wider --limit."
        )
        return

    typer.echo(
        f"\nAggregate over {r['n_qualifying']} qualifying products "
        f"(min lift >= {min_lift:.1f}x, lead window = {lead} days):\n"
    )
    typer.echo(f"  Spikes evaluated:   {r['total_spikes']:>5}")
    typer.echo(f"  Signals fired:      {r['total_signals']:>5}")
    typer.echo(
        f"  Spikes caught:      {r['total_caught']:>5}   "
        f"recall    = {r['recall'] * 100:.1f}%"
    )
    typer.echo(
        f"  Signal hits:        {r['total_hits']:>5}   "
        f"precision = {r['precision'] * 100:.1f}%"
    )
    typer.echo(f"  Median lead time:   {r['median_lead']:>4.0f} days")
    if r["base_rate"] is not None:
        lift_str = f"{r['lift']:.1f}x" if r["lift"] is not None else "n/a"
        typer.echo(
            f"  Base rate (chance): {r['base_rate'] * 100:>4.1f}%   "
            f"lift = {lift_str}"
        )

    typer.echo("")
    lead_str = f"{r['median_lead']:.0f} days" if r["has_positive_lead"] else "zero or negative"
    lift_str = f"{r['lift']:.1f}x" if r["lift"] is not None else "n/a"
    if r["beats_chance"] and r["has_positive_lead"]:
        typer.echo(
            f"Verdict: YES — early signals arrive {lead_str} ahead of spikes "
            f"and beat chance ({lift_str} lift, {r['precision'] * 100:.0f}% precision "
            f"vs {r['base_rate'] * 100:.0f}% base rate)."
        )
    elif r["beats_chance"]:
        typer.echo(
            f"Verdict: MIXED — signals beat chance ({lift_str} lift) "
            f"but median lead time is {lead_str} (signals may arrive same day or after)."
        )
    elif r["has_positive_lead"]:
        typer.echo(
            f"Verdict: MIXED — positive lead time ({lead_str}) "
            f"but precision does not beat chance (lift {lift_str})."
        )
    else:
        typer.echo(
            "Verdict: NO — signals do not beat chance and have no lead time. "
            "Try widening --days or lowering --min-lift."
        )

    typer.echo("\nPer-product breakdown:")
    for p in r["per_product"]:
        lift_s = f"{p['lift']:.1f}x" if p["lift"] is not None else "n/a"
        typer.echo(
            f"  {p['product'].replace('_', ' '):<30}  "
            f"spikes={p['n_spikes']}  "
            f"recall={p['recall'] * 100:.0f}%  "
            f"prec={p['precision'] * 100:.0f}%  "
            f"lead={p['median_lead']:.0f}d  "
            f"lift={lift_s}"
        )

    typer.echo(
        "\nHonest note: backtest on attention-proxy data, not literal sales. "
        "Past signal performance does not guarantee future results."
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
