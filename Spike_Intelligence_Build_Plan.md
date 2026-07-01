# Spike Intelligence — Claude Code Build Plan

A terse, copy-paste prompt sequence for building the system in Claude Code. Paste the prompts one at a time, in order. Each is scoped to a vertical slice with acceptance criteria, so you can verify and commit before moving on.

---

## 0. What you're building

A **demand-intelligence system**: a continuously-learning causal model of how demand forms. Spike prediction is one slice; the broader "demand-OS" questions (factor contribution, cross-industry drivers, drift over time, customer-group / channel lift) are the **same machinery surfaced differently**.

**The one invariant that makes the OS free instead of a rebuild:** the data model carries a `segment` (and `channel`) dimension everywhere, and **every attribution is persisted as a first-class row** — not discarded after a prediction. Get this right in Prompt 0 and every "OS" query is just a `GROUP BY` over data you already compute.

**Build order:** prediction core first (fast feedback), on an OS-ready schema. **Synthetic-data-first** — generate data with *known* injected spikes and *known* causal factors so the detector and attributor are validated against ground truth before any paid API is touched.

---

## 1. Stack & repo layout (decided — don't re-litigate in the prompts)

- **Python 3.11**, `uv` for env/deps, `ruff` + `pytest` + `pre-commit`.
- **Store:** DuckDB (single file, SQL, zero infra); raw pulls cached as Parquet.
- **Modelling:** `statsmodels` (STL baseline), `tfp-causalimpact` (Google's BSTS + spike-and-slab) for attribution. Note it pulls TensorFlow; if you want lean, swap to `causalimpact` (pycausalimpact) — same interface, lighter. Keep attribution behind an interface so the backend is swappable.
- **Schemas/config:** `pydantic` v2 + `pydantic-settings`. **CLI:** `typer`. **Optional surface:** Streamlit.

```
demand/
  ingest/        # Source ABC + connectors (synthetic, trends, gdelt, keepa, weather)
  detect/        # baseline + spike detector
  attribute/     # factor alignment + causal attribution (interface + tfp backend)
  signatures/    # aggregation into reusable factor signatures
  predict/       # forward predictor + backtest harness
  feedback/      # online recalibration
  store/         # DuckDB schema, pydantic models, query layer
  cli.py
tests/
data/            # duckdb file + parquet cache (gitignored)
CLAUDE.md
```

---

## 2. How to drive Claude Code (meta-rules)

- One prompt → one PR/commit. Make it write tests for each slice and run them before committing.
- Synthetic-first: nothing touches a paid API until Prompts 0–4 pass on synthetic ground truth.
- Gate real connectors behind env keys; no secrets in the repo.
- **Pre-register** the backtest config (hash it, log it) before you look at real-data results, so you can't move the goalposts.
- Keep `CLAUDE.md` current — it's the agent's memory across sessions.
- Drop the concept doc (`Spike_Intelligence_Concept.docx`) into the repo root too, for context.

---

## 3. Drop-in `CLAUDE.md` (paste this into the repo first)

```markdown
# Project: Spike Intelligence (demand-intelligence system)

## Goal
Detect demand spikes from public proxy signals, attribute them to environmental
factors causally, generalize into reusable signatures, then forward-predict spikes.
Spike prediction is the first slice of a broader demand-modeling system.

## Non-negotiable invariants
1. Demand and factor data are PUBLIC PROXIES (Amazon Sales Rank via Keepa, Google
   Trends, review velocity, social-video curves), never literal unit sales.
2. The schema carries `segment` and `channel` dimensions on EVERY fact table.
3. Attribution outputs (per-factor effect size, posterior inclusion prob, lag) are
   PERSISTED as first-class rows in `attributions`, never thrown away.
4. Attribution is probabilistic, never asserted as proof.
5. Validate on synthetic ground truth before real data; pre-register backtest config.

## Data model (DuckDB)
- observations(product_id, segment, metric, source, ts, value)
- factors(factor_id, category, channel, segment, source, ts, value)
- spikes(spike_id, product_id, segment, onset_ts, severity, magnitude,
         persistence, acceleration, detector_version)
- attributions(spike_id, factor_id, effect_size, posterior_incl_prob, lag_days,
         model_version, run_ts)              # <- the OS lives here
- signatures(signature_id, factor_set, category_scope, lag_dist, hit_rate, support_n)
- predictions(pred_id, product_id, segment, made_ts, window_start, window_end,
         prob, signature_id, status)
- outcomes(pred_id, realized, realized_ts, error)

## Stack
Python 3.11, uv, DuckDB+Parquet, statsmodels, tfp-causalimpact (swappable),
pydantic v2, typer, pytest, ruff. Synthetic data is the default source.

## Definitions
- Spike: residual z (robust, via MAD) >= k for >= d consecutive days AND accelerating
  (positive 2nd difference of growth rate). Severity = magnitude * persistence * accel.
- Attribution: BSTS counterfactual with spike-and-slab variable selection over the
  factor matrix in window [-14d, +3d] around onset.

## Workflow
One vertical slice per PR, tests first, commit on green. Keep this file updated.
```

---

## 4. The build sequence

### PROMPT 0 — Scaffold
```
Set up the repo per CLAUDE.md. Use uv, Python 3.11, the package layout in CLAUDE.md,
ruff + pytest + pre-commit, a Makefile (`make setup/test/lint`). Implement the DuckDB
schema from CLAUDE.md as pydantic v2 models in demand/store/, with a `demand init`
typer command that creates the database. Add a Source ABC in demand/ingest/base.py
(methods: name(), pull(spec) -> rows mapped to observations/factors). Config via
pydantic-settings reading .env. No business logic yet.
Acceptance: `make test` green; `demand init` creates data/demand.duckdb with all 8
tables; Source ABC importable; segment+channel columns present on every fact table.
```

### PROMPT 1 — Synthetic ground truth
```
Implement a SyntheticSource (Source subclass) that generates a configurable universe:
N products across M categories, each an observations series = trend + weekly
seasonality + noise. Inject spikes at known timestamps caused by specific factors at
known lags; also emit those factors into `factors` (with segment/channel tags), plus
decoy factors that cause nothing. Persist a hidden `_ground_truth(spike, causal
factor_id, lag_days)` table for scoring. Deterministic via --seed.
Acceptance: `demand synth --products 500 --seed 1` populates observations/factors and
_ground_truth; re-running with same seed is identical; decoys present; >=1 multi-factor
spike included.
```

### PROMPT 2 — Spike detector
```
Implement demand/detect/: STL (statsmodels) baseline -> residual -> robust z via MAD
(z = r / (1.4826*MAD)) -> fire when z>=k for >=d consecutive days AND growth rate
2nd-difference > 0. Compute severity = magnitude*persistence*acceleration. Write rows
to `spikes`. Params (k, d, ...) in config. Add a backtest that scores DETECTION
(precision/recall/F1) of detected spikes vs _ground_truth timestamps.
Acceptance: detection F1 >= 0.90 on `demand synth --products 500 --seed 1` at default
params; unit tests for the z/accel logic on hand-built series.
```

### PROMPT 3 — Causal attribution
```
Implement demand/attribute/: for each spike, build the factor matrix over [-14d,+3d]
around onset; run BSTS with spike-and-slab (tfp-causalimpact) behind an Attributor
interface (so the backend is swappable). Persist per-factor effect_size,
posterior_incl_prob, and estimated lag_days into `attributions`. Add a scorer:
top-attributed factor vs the injected causal factor in _ground_truth.
Acceptance: top-1 attribution matches the injected cause for >= 70% of synthetic
single-cause spikes; multi-cause spikes recover >=1 true cause; attributions persisted
with model_version + run_ts.
```

### PROMPT 4 — Signatures + the demand-OS query layer
```
Implement demand/signatures/: aggregate `attributions` into `signatures`
(recurring factor_set -> lag_dist, hit_rate, support_n). Then build demand/store/
queries.py answering, as functions + `demand ask` CLI subcommands:
(a) contribution per factor for a product/spike,
(b) cross-category factor importance (group attributions by category),
(c) factor importance over time (group by run_ts),
(d) demand drivers by segment (customer groups),
(e) lift by channel.
These are GROUP BYs over attributions/signatures — no new modelling.
Acceptance: on a synthetic universe with a known dominant cross-category factor, query
(b) ranks it #1; (d)/(e) return correct per-segment/per-channel breakdowns; each query
has a test against constructed ground truth.
```

### PROMPT 5 — Real connectors
```
Implement Source connectors behind the ABC, mapping into observations/factors with
segment/channel tags; SyntheticSource stays the default fallback:
- GoogleTrendsSource (trendspyg, free) incl. geo breakdown -> segment dimension,
- GDELTSource (DOC 2.0 API, free) -> news volume/tone factors,
- KeepaSource (paid, key-gated, optional) -> sales-rank velocity proxy + review
  velocity + price factors,
- WeatherSource (Open-Meteo, free).
Keys from .env; integration tests use recorded/mocked responses; respect rate limits.
Acceptance: `demand pull --source trends --keyword "<x>"` writes rows; missing key ->
clean skip, not crash; no secrets committed; synthetic still default.
```

### PROMPT 6 — Forward predictor + backtest harness
```
Implement demand/predict/: stream factors -> match against `signatures` -> emit
`predictions` (window + prob + signature_id). Build a backtest harness that, given a
PRE-REGISTERED config (hash logged before run), reports precision@k, recall, median
lead time, a calibration curve, and a simulated net P&L after assumed costs/fees and
miss rate. Writes predictions/outcomes.
Acceptance: backtest produces a reproducible report on a held-out synthetic split;
config hash logged; lead-time and calibration computed; rerun = identical numbers.
```

### PROMPT 7 — Feedback loop
```
Implement demand/feedback/: score predictions vs outcomes, Bayesian-update signature
hit-rates / factor weights, and expose factor-importance-over-time (versioned weights).
Acceptance: running feedback after outcomes land shifts weights toward factors that
verified; `demand ask importance-over-time` returns a timeline; weights are versioned
and auditable.
```

### PROMPT 8 — (Optional) thin surface
```
Add a Streamlit app reading the DuckDB store: watchlist + live spike feed, factor-
contribution view, cross-industry factor ranking, segment/channel breakdown, and
importance-over-time. Read-only over the store; no recomputation in the UI.
Acceptance: all five demand-OS views render from the store on the synthetic universe.
```

---

## 5. Where your five questions get answered

| Your question | Lives in | How |
|---|---|---|
| Will this product spike? | `predict/` (Prompt 6) | signature match → probability + window |
| How much does each factor contribute? | `attributions` (Prompt 3) | `effect_size`, `posterior_incl_prob` per factor |
| Which factors drive demand across industries? | `signatures` (Prompt 4) | attributions grouped by category |
| Which customer groups / channels drive demand? | `segment`/`channel` dims (Prompts 4–5) | attributions grouped by segment/channel |
| How do these relationships change over time? | `feedback/` (Prompt 7) | factor importance over `run_ts` |

---

## 6. Gate before spending money / going live

Don't wire Keepa or attempt Model B until **Prompt 6's backtest** clears a pre-set bar on real data: positive precision@k, **non-trivial median lead time** (if it's ~0, there's no business), and a positive simulated P&L after costs. That gate is the whole point of building synthetic-first.
```
