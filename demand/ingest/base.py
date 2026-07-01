"""Source abstraction. Real connectors (Google Trends, GDELT, Keepa, weather) get
added behind this interface in Prompt 5; SyntheticSource is the default fallback."""
from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Source(ABC):
    """A data source returns normalized frames keyed by target table.

    fetch() -> {"observations": df, "factors": df, "_ground_truth": df?}
    Column order must match the DDL in demand/store/schema.py.
    """

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def fetch(self) -> dict[str, "pd.DataFrame"]:
        ...
