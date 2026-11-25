from __future__ import annotations

import duckdb


class WindowBuilder:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")

    def build(self):

        self.con.execute("""
DROP TABLE IF EXISTS spike_windows
""")

        self.con.execute("""

CREATE TABLE spike_windows AS

SELECT

product_id,

segment,

spike_date,

severity,

magnitude,

persistence,

acceleration,

event_id,

observed_at,

days_before,

factor_type,

factor_value,

weight,

CASE

WHEN days_before<=1 THEN '1D'

WHEN days_before<=3 THEN '3D'

WHEN days_before<=7 THEN '7D'

WHEN days_before<=14 THEN '14D'

WHEN days_before<=30 THEN '30D'

WHEN days_before<=60 THEN '60D'

WHEN days_before<=90 THEN '90D'

ELSE 'OUTSIDE'

END AS lead_window

FROM spike_factor_links

WHERE days_before BETWEEN 0 AND 90

""")

        print()

        print(

            self.con.execute("""

SELECT

lead_window,

COUNT(*)

FROM spike_windows

GROUP BY lead_window

ORDER BY

CASE lead_window

WHEN '1D' THEN 1

WHEN '3D' THEN 2

WHEN '7D' THEN 3

WHEN '14D' THEN 4

WHEN '30D' THEN 5

WHEN '60D' THEN 6

WHEN '90D' THEN 7

ELSE 8

END

""").fetchdf()

        )


if __name__=="__main__":

    WindowBuilder().build()
