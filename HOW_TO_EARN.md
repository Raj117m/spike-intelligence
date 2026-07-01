# How to actually use the radar (read this honestly)

## What the one command does

```bash
cd ~/spike-intelligence
uv run demand radar
```

It scans what's trending, finds **forward opportunities** (a topic whose related factor is
rising *right now*, where that factor has *historically* predicted that topic's spikes),
labels each **PROVEN** or **unproven**, grades its own past calls, and saves a dated report
in the `reports/` folder.

## What it is — and is not

It **is** a lead-finder: it points at places where public attention is starting to move
early, and tells you how trustworthy that signal has been before. That is genuinely useful
and most people don't have it.

It is **not** a money machine. Be clear-eyed:

- It measures **attention** (a proxy for demand), not actual sales.
- A "PROVEN" tag means the signal beat chance *historically* — not a promise about the future.
- It cannot place orders, hold inventory, or know your costs. **It will not earn money by
  itself.**

## The honest path from a lead to actual earnings

1. **Start from a PROVEN opportunity** in the report (ignore "unproven" until you trust the tool).
2. **Sanity-check it like a human** — is there a real product behind the trend people would buy?
3. **Source small and cheap.** Buy a *small* test quantity from a low-cost supplier. Never
   bet big on a single signal.
4. **Sell where the attention is** (the marketplace/platform where that audience shops).
5. **Respect platform rules** — marketplaces penalise price-gouging and manipulation.
6. **Track your real result** and compare it to what the radar predicted. Over time the
   radar's own "track record" line tells you how much to trust it.

The analytics reduce *which-product* risk. They do **not** remove the ordinary risks of
selling (suppliers, shipping, returns, fees, competition). Start with money you can afford
to lose, and scale only what actually works.

## Make it run itself (optional)

Run it each morning by hand, or schedule it. To run daily at 8am, in Terminal type
`crontab -e`, then add this line (replace the path if your project lives elsewhere):

```
0 8 * * * cd $HOME/spike-intelligence && /opt/homebrew/bin/uv run demand radar >> reports/cron.log 2>&1
```

(Save and exit. On Intel Macs `uv` may be at `/usr/local/bin/uv` — check with `which uv`.)

## One-line truth

The radar finds and grades opportunities for free; **you** turn a good lead into money by
acting carefully and small. Treat it as a smart scout, not a guarantee.
