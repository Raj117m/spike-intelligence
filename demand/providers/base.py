"""
Base interface for all external knowledge providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class ProviderResult:

    source: str

    query: str

    confidence: float

    data: dict


class Provider(ABC):

    @abstractmethod
    def search(self, query: str) -> list[ProviderResult]:
        ...
