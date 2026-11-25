from __future__ import annotations

from demand.world_state.node import WorldNode
from demand.world_state.edge import WorldEdge


class WorldStateGraph:

    def __init__(self):

        self.nodes = {}

        self.edges = []

    def add_node(self, node: WorldNode):

        self.nodes[node.id] = node

    def add_edge(self, edge: WorldEdge):

        self.edges.append(edge)

    def neighbours(self, node_id):

        return [

            e.target

            for e in self.edges

            if e.source == node_id

        ]

    def summary(self):

        return {

            "nodes": len(self.nodes),

            "edges": len(self.edges),

        }
