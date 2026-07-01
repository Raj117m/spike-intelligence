# Spike Intelligence — starter

A pre-built scaffold (Prompts 0–1) for the demand-intelligence system. It creates the
database, defines the data model, and generates synthetic data with **known** spikes and
**known** causes — so the detector and attributor you build next can be scored against
truth before any paid API is used.

## Run it (after `uv` is installed — see the setup guide)

```bash
uv sync                                  # create env + install deps
uv run demand init                       # create the database (8 tables)
uv run demand synth --products 500 --seed 1   # generate synthetic data
uv run demand info                       # see row counts + injected spikes
uv run pytest -q                         # optional: run the tests
```

If `demand info` shows ~90,000 observations and a list of injected spikes, everything
works.

## What's here
- `demand/store/schema.py` — DuckDB schema (segment/channel on every table; attributions persisted)
- `demand/ingest/base.py` — `Source` interface for data connectors
- `demand/ingest/synthetic.py` — synthetic ground-truth generator
- `demand/cli.py` — `init`, `synth`, `info`
- `tests/` — smoke tests
- `CLAUDE.md` — project brief + the resume checklist for Claude Code
- `Spike_Intelligence_Build_Plan.md` — the full prompt sequence (Prompts 2–8)

## Resume in Claude Code
When your usage limit resets, from this folder run `claude`, then paste **Prompt 2**
from `Spike_Intelligence_Build_Plan.md`. Continue one prompt at a time.
