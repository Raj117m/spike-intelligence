from __future__ import annotations

from abc import ABC, abstractmethod


class Importer(ABC):
    """
    Base class for all data importers.
    """

    @abstractmethod
    def import_data(self) -> None:
        """Import data into DuckDB."""
        raise NotImplementedError
