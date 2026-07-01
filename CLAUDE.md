# Project: Spike Intelligence (demand-intelligence system)

## Goal
Detect demand spikes from public proxy signals, attribute them to environmental
factors causally, generalize into reusable signatures, then forward-predict spikes.
Spike prediction is the first slice of a broader demand-modeling system.

## Status
Real, end-to-end on free data. Schema + detector (STL + robust MAD z + accel, F1 ~0.8) +
REAL connector (Wikipedia pageviews, no key) + REAL attribution v1 (`explain`): for a
product it pulls related-topic attention as environmental factors and ranks which factor
LED each spike (lead/lag association), persisting to `attributions`. Also emits a forward
"live signal" (a factor rising now). CLI: init, synth, info, detect, score-detect,
pull-wiki, explain, discover, watch. Reliability+discovery layer (free Wikimedia):
resolve_title (loose text -> real page), related_titles (auto-factors via 'morelike'),
top_articles (trending firehose). attributor split into analyze() (pure, no I/O),
explain() (resolve + persist), watch() (scan firehose -> per-topic driver). `watch` is
the live "what's spiking and why" board, fully automatic. Plus `backtest` (evaluate/):
causal trailing-z signal -> predict spike within `lead` days; reports precision, recall,
median lead, base rate, and LIFT over chance (the key metric). Plus `radar` (radar.py):
THE one command - discover -> detect -> attribute -> confidence (lift) -> forward
opportunities (factor rising now + proven) -> writes reports/radar_DATE.md and logs
predictions to reports/opportunities_log.jsonl, grading matured calls on later runs
(self-scoring track record = honest feedback loop). HOW_TO_EARN.md = plain-English usage.
17 tests pass. Next: causal BSTS attribution; Trends/GDELT/weather factors; product-only filter.

## Non-negotiable invariants
1. Demand and factor data are PUBLIC PROXIES (Amazon Sales Rank via Keepa, Google
   Trends, review velocity, social-video curves), never literal unit sales.
2. The schema carries `segment` and `channel` dimensions on EVERY fact table.
3. Attribution outputs (per-factor effect size, posterior inclusion prob, lag) are
   PERSISTED as first-class rows in `attributions`, never thrown away.
4. Attribution is probabilistic, never asserted as proof.
5. Validate on synthetic ground truth before real data; pre-register backtest config.

## Data model (DuckDB, see demand/store/schema.py)
observations, factors, spikes, attributions, signatures, predictions, outcomes,
_ground_truth (hidden, synthetic only). The demand-OS questions are GROUP BYs over
`attributions` + `signatures` sliced by segment/channel/category.

## Definitions
- Spike: robust residual z (via MAD) >= spike_k for >= spike_min_days consecutive days
  AND accelerating (positive 2nd difference of growth rate). Severity =
  magnitude * persistence * acceleration.
- Attribution: BSTS counterfactual with spike-and-slab variable selection over the
  factor matrix in window [-14d, +3d] around onset.

## Stack
Python 3.11, uv, DuckDB+Parquet, statsmodels (STL), tfp-causalimpact (swappable for
`causalimpact`), pydantic v2, typer, pytest, ruff. Synthetic data is the default source.

## Build sequence (resume here)
- [x] Prompt 0  scaffold + schema + Source ABC + CLI
- [x] Prompt 1  synthetic ground-truth generator
- [x] Prompt 2  spike detector (STL baseline + robust-z + accel) -> `spikes`; scored
      DETECTION precision/recall vs `_ground_truth` (F1 ~0.8 at k=3, d=2).
- [~] Prompt 3  attribution v1 DONE (lead/lag association, real data, `explain`,
      persists `attributions`). TODO: upgrade to causal BSTS + score cause recovery.
- [ ] Prompt 4  signatures + demand-OS query layer (contribution, cross-industry,
      over-time, by segment, by channel).
- [~] Prompt 5  real connectors: Wikipedia pageviews DONE (free, no key, `pull-wiki`);
      Google Trends / GDELT / Keepa / weather still to add behind the Source ABC.
- [x] Prompt 6  forward predictor: `watch` live board + `backtest` harness DONE
      (precision, recall, lead time, base rate, LIFT; causal trailing-z signal).
- [x] Prompt 7  feedback loop: `radar` logs predictions + grades matured calls into a
      running track record (reports/opportunities_log.jsonl). TODO: weight recalibration.
- [ ] Prompt 8  optional Streamlit surface.

Full prompt text is in Spike_Intelligence_Build_Plan.md (repo root).

## Workflow
One vertical slice per PR, tests first, commit on green. Keep this file updated.
