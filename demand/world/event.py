from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorldEvent:

    id: int

    date: int

    actor1: str | None

    actor2: str | None

    event_code: str

    mentions: int

    tone: float

    location: str | None

    source_url: str | None
