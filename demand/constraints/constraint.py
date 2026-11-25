"""
Universal Constraint Model

Every demand begins with one or more constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Constraint:

    id: str

    name: str

    category: str

    description: str

    physical_domain: str

    affects: list[str] = field(default_factory=list)

    causes: list[str] = field(default_factory=list)

    relieved_by: list[str] = field(default_factory=list)

    measurable_by: list[str] = field(default_factory=list)

    confidence: float = 0.0

    validated: bool = False
