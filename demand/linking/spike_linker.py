from __future__ import annotations

import duckdb


class SpikeLinker:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        print()
        print("Building spike links...")
        print()

        self.con.execute("""

DROP TABLE IF EXISTS spike_factor_links

""")

        self.con.execute("""

CREATE TABLE spike_factor_links AS

SELECT

    s.spike_id,

    s.product_id,

    s.segment,

    s.onset_ts AS spike_date,

    s.severity,

    s.magnitude,

    s.persistence,

    s.acceleration,

    f.event_id,

    f.observed_at,

    date_diff(
        'day',
        f.observed_at,
        s.onset_ts
    ) AS days_before,

    f.factor_type,

    f.factor_value,

    f.weight

FROM spikes s

INNER JOIN factor_store f

ON f.observed_at
BETWEEN
    s.onset_ts - INTERVAL 90 DAY
AND
    s.onset_ts

""")
        self.con.execute("""

CREATE INDEX IF NOT EXISTS idx_spike_links_product

ON spike_factor_links(product_id)

""")

        self.con.execute("""

CREATE INDEX IF NOT EXISTS idx_spike_links_event

ON spike_factor_links(event_id)

""")

        self.con.execute("""

CREATE INDEX IF NOT EXISTS idx_spike_links_factor

ON spike_factor_links(factor_type,factor_value)

""")

        self.con.execute("""

CREATE INDEX IF NOT EXISTS idx_spike_links_date

ON spike_factor_links(observed_at)

""")

        print("Finished building links.")
        print()

        total = self.con.execute("""

SELECT COUNT(*)

FROM spike_factor_links

""").fetchone()[0]

        print(f"Total links : {total:,}")

        print()

        print(

            self.con.execute("""

SELECT

factor_type,

COUNT(*) AS links

FROM spike_factor_links

GROUP BY factor_type

ORDER BY links DESC

LIMIT 20

""").fetchdf()

        )

        print()
        summary = self.con.execute("""

SELECT

    MIN(days_before) AS min_days,

    MAX(days_before) AS max_days,

    COUNT(DISTINCT spike_id) AS linked_spikes,

    COUNT(DISTINCT event_id) AS linked_events

FROM spike_factor_links

""").fetchdf()

        print(summary)

        print()

        sample = self.con.execute("""

SELECT

    spike_id,

    product_id,

    spike_date,

    event_id,

    observed_at,

    days_before,

    factor_type,

    factor_value,

    weight

FROM spike_factor_links

ORDER BY spike_date, days_before

LIMIT 20

""").fetchdf()

        print(sample)

        print()

        return summary
if __name__ == "__main__":

    SpikeLinker().build()
