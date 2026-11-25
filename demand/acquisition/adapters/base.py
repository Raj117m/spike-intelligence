from __future__ import annotations

from abc import ABC, abstractmethod


class DatasetAdapter(ABC):

    @abstractmethod
    def check(self):
        """
        Return whether a newer version exists.
        """
        ...

    @abstractmethod
    def latest_version(self):
        ...

    @abstractmethod
    def download(self):
        ...

    @abstractmethod
    def verify(self):
        ...

    @abstractmethod
    def normalize(self):
        ...

    @abstractmethod
    def metadata(self):
        ...
