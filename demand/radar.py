"""One-command opportunity radar.

Combines everything: discover trending topics -> detect spikes -> attribute the driver
-> score how trustworthy that driver has been historically (backtest LIFT) -> surface
forward opportunities (a trustworthy factor rising right now). It also LOGS every call
and, on later runs, checks whether past calls came true - so it accumulates a real,
verifiable track record (this is the honest version of "it trains itself").

HONEST SCOPE: this finds where ATTENTION is spiking early and how reliable each signal
has been. It does NOT guarantee sales or profit. Acting on a lead (sourcing/selling) is
a separate, real-world, capital-at-risk step. Treat it as a lead-finder; start small.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta

import pandas as pd

from .attribute.attributor import analyze
from .detect.detector import find_spikes
from .evaluate.backtest import evaluate_signal
from .ingest.wikipedia import fetch_series, related_titles, top_articles

LIVE_Z = 2.5


def _log_path(reports_dir: str) -> str:
    return os.path.join(reports_dir, "opportunities_log.jsonl")


def _read_log(reports_dir: str) -> list[dict]:
    path = _log_path(reports_dir)
    if not os.path.exists(path):
        return []
    out = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def _write_log(reports_dir: str, rows: list[dict]) -> None:
    os.makedirs(reports_dir, exist_ok=True)
    with open(_log_path(reports_dir), "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def _score_matured(reports_dir: str, max_check: int = 6, k: float = 3.0, d: int = 2) -> dict:
    """Grade past predictions whose window has elapsed: did the topic actually spike?"""
    log = _read_log(reports_dir)
    today = date.today()
    checked = 0
    for entry in log:
        if entry.get("outcome") is not None:
            continue
        try:
            predict_by = datetime.strptime(entry["predict_by"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            entry["outcome"] = "skip"
            continue
        if predict_by >= today:
            continue  # not matured yet
        if checked >= max_check:
            break
        checked += 1
        s = fetch_series(entry["topic"], days=120)
        if s.empty:
            entry["outcome"] = "no_data"
            continue
        vals = s["value"].to_numpy()
        dates = list(pd.to_datetime(s["ts"]).dt.date)
        run_d = datetime.strptime(entry["run_date"], "%Y-%m-%d").date()
        hit = False
        for sp in find_spikes(vals, k, d):
            od = dates[sp["peak"]]
            if run_d < od <= predict_by:
                hit = True
                break
        entry["outcome"] = "hit" if hit else "miss"
    _write_log(reports_dir, log)

    scored = [e for e in log if e.get("outcome") in ("hit", "miss")]
    hits = sum(1 for e in scored if e["outcome"] == "hit")
    return {"scored": len(scored), "hits": hits,
            "rate": (hits / len(scored)) if scored else None}


def radar(limit: int = 8, days: int = 365, recent_days: int = 30, max_factors: int = 3,
          lead: int = 10, threshold: float = 3.0, min_lift: float = 1.2,
          reports_dir: str = "reports", score: bool = True) -> dict:
    track = _score_matured(reports_dir) if score else {"scored": 0, "hits": 0, "rate": None}

    opportunities, recent = [], []
    for name, views in top_articles(limit):
        try:
            facs = related_titles(name.replace("_", " "), limit=max_factors)
            res = analyze(name, facs, days=days)
        except Exception:  # noqa: BLE001
            continue
        if "error" in res or not res["spikes"]:
            continue

        df = res["frame"]
        prod = res["product"]
        ev = evaluate_signal(df[prod].to_numpy(),
                             [df[c].to_numpy() for c in res["loaded"]],
                             lead=lead, threshold=threshold) if res["loaded"] else {}
        lift = ev.get("lift")
        med_lead = ev.get("median_lead", 0.0)

        last = pd.Timestamp(res["last_date"])
        recent_sp = None
        for sp in sorted(res["spikes"], key=lambda x: pd.Timestamp(x["onset"]), reverse=True):
            if (last - pd.Timestamp(sp["onset"])).days <= recent_days:
                recent_sp = sp
                break
        if recent_sp:
            drv = recent_sp["candidates"][0] if recent_sp["candidates"] else None
            recent.append({"topic": name, "onset": str(recent_sp["onset"]),
                           "strength": recent_sp["magnitude"], "driver": drv})

        # forward opportunity: a factor is rising NOW and it has historical lift
        live = res["live"]
        proven = lift is not None and lift >= min_lift
        if live:
            opportunities.append({
                "topic": name, "views": views,
                "rising_factor": live[0]["factor"], "rising_z": live[0]["z"],
                "lift": lift, "confidence": "proven" if proven else "unproven",
                "expected_lead_days": med_lead,
                "score": (lift if proven else 1.0) * live[0]["z"],
            })

    opportunities.sort(key=lambda r: -r["score"])
    recent.sort(key=lambda r: -r["strength"])

    # log this run's opportunities so we can grade them later
    new_log = _read_log(reports_dir)
    run_date = date.today()
    predict_by = run_date + timedelta(days=lead)
    for o in opportunities:
        new_log.append({"run_date": run_date.isoformat(), "topic": o["topic"],
                        "rising_factor": o["rising_factor"], "lift": o["lift"],
                        "predict_by": predict_by.isoformat(), "outcome": None})
    _write_log(reports_dir, new_log)

    result = {"generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "track": track, "opportunities": opportunities, "recent": recent,
              "lead": lead, "min_lift": min_lift}
    result["report_path"] = _write_report(reports_dir, result)
    return result


def _write_report(reports_dir: str, r: dict) -> str:
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"radar_{date.today().isoformat()}.md")
    lines = [f"# Opportunity radar - {r['generated']}", ""]
    t = r["track"]
    if t["rate"] is not None:
        lines.append(f"**Track record so far:** {t['hits']}/{t['scored']} past calls came "
                     f"true ({t['rate'] * 100:.0f}%).")
    else:
        lines.append("**Track record so far:** not enough matured predictions yet.")
    lines += ["", f"## Forward opportunities (factor rising now; predict ~{r['lead']} days)", ""]
    if r["opportunities"]:
        lines.append("| Topic | Rising factor | Confidence | Hist. lift | Exp. lead |")
        lines.append("|---|---|---|---|---|")
        for o in r["opportunities"]:
            lift = f"{o['lift']:.1f}x" if o["lift"] is not None else "n/a"
            lines.append(f"| {o['topic'].replace('_', ' ')} | "
                         f"{o['rising_factor'].replace('_', ' ')} | {o['confidence']} | "
                         f"{lift} | {o['expected_lead_days']:.0f}d |")
    else:
        lines.append("_No forward opportunities right now._")
    lines += ["", "## Recently spiked (what just moved)", ""]
    for x in r["recent"][:10]:
        drv = (x["driver"]["factor"].replace("_", " ") if x["driver"] else "no clear factor")
        lines.append(f"- **{x['topic'].replace('_', ' ')}** spiked {x['onset']} "
                     f"(z={x['strength']:.1f}) - likely driver: {drv}")
    lines += ["", "> Honest scope: attention signals on free data, not a profit guarantee. "
              "Acting on a lead is a separate, real-world, capital-at-risk step. Start small."]
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path
