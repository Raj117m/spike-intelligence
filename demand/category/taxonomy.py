"""
Category taxonomy engine.
"""

from __future__ import annotations

from collections import defaultdict


class Taxonomy:
    """
    Stores parent/child category relationships.

    Example:

        Sporting Event
              |
          Football
              |
       FIFA World Cup
    """

    def __init__(self) -> None:
        self._parent: dict[str, str | None] = {}
        self._children: dict[str, set[str]] = defaultdict(set)

    def add_category(self, name: str, parent: str | None = None) -> None:
        self._parent[name] = parent
        if parent is not None:
            self._children[parent].add(name)

    def parent(self, name: str) -> str | None:
        return self._parent.get(name)

    def children(self, name: str) -> list[str]:
        return sorted(self._children.get(name, set()))

    def ancestors(self, name: str) -> list[str]:
        out = []
        current = self.parent(name)
        while current is not None:
            out.append(current)
            current = self.parent(current)
        return out

    def descendants(self, name: str) -> list[str]:
        out = []

        def walk(node: str):
            for child in self.children(node):
                out.append(child)
                walk(child)

        walk(name)
        return out

    def is_descendant(self, child: str, ancestor: str) -> bool:
        return ancestor in self.ancestors(child)
