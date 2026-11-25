"""
Abstract environmental data source.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import EnvironmentalSignal


class EnvironmentalSource(ABC):
    """
    Every live environmental source must implement this interface.
    """

    @abstractmethod
    def name(self) -> str:
        """Human-readable source name."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self) -> list[EnvironmentalSignal]:
        """
        Return normalized environmental signals.
        """
        raise NotImplementedError
