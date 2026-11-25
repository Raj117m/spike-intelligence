from demand.world_state.graph import WorldStateGraph
from demand.world_state.node import WorldNode
from demand.world_state.edge import WorldEdge

g = WorldStateGraph()

g.add_node(
    WorldNode(
        "storm",
        "event",
        "Storm",
    )
)

g.add_node(
    WorldNode(
        "electricity",
        "constraint",
        "Electrical Supply Constraint",
    )
)

g.add_edge(

    WorldEdge(

        "storm",

        "electricity",

        "activates",

        0.95,

    )

)

print(g.summary())

print()

print(g.neighbours("storm"))
